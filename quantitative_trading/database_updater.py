print("腳本開始執行...")
import configparser
print("成功導入 configparser")
import pandas as pd
print("成功導入 pandas")
import yfinance as yf
print("成功導入 yfinance")
from sqlalchemy import create_engine, text
from sqlalchemy.types import NVARCHAR, Date, Float, BIGINT
print("成功導入 sqlalchemy")
import urllib
print("成功導入 urllib")
import time
print("成功導入 time")
from datetime import datetime, timedelta # Import datetime and timedelta

print("所有模組導入成功，準備定義 Class...")

class DatabaseUpdater:
    def __init__(self, config_path='config.ini'):
        print("DatabaseUpdater Class 初始化開始...")
        self.engine = self._create_db_engine(config_path)
        print("DatabaseUpdater Class 初始化完成。")

    def _create_db_engine(self, config_path):
        print("開始讀取設定檔...")
        config = configparser.ConfigParser()
        config.read(config_path)
        db_config = config['Database']
        print("設定檔讀取完畢。")

        server = db_config['Server']
        database = db_config['Database']
        username = db_config['Username']
        password = db_config['Password']
        driver = db_config['Driver'].replace(' ', '+')

        print("準備建立資料庫連線字串...")
        encoded_password = urllib.parse.quote_plus(password)
        connection_string = f"mssql+pyodbc://{username}:{encoded_password}@{server}/{database}?driver={driver}"
        print("連線字串建立完成，準備連線...")
        
        try:
            engine = create_engine(connection_string)
            with engine.connect() as connection:
                print("資料庫連線成功！")
            return engine
        except Exception as e:
            print(f"資料庫連線失敗: {e}")
            return None

    def get_stock_list_from_twse(self):
        """從台灣證券交易所網站獲取上市公司列表"""
        try:
            url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=open_data"
            df = pd.read_csv(url)
            stock_list = df['證券代號'].astype(str).tolist()
            print(f"成功獲取 {len(stock_list)} 筆上市股票代碼。")
            return stock_list
        except Exception as e:
            print(f"無法獲取股票列表: {e}")
            return []
            
    def get_stock_list_from_db(self):
        """從資料庫獲取已存在的股票列表"""
        if not self.engine:
            return []
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT DISTINCT StockID FROM daily_prices"))
                stock_list = [row[0] for row in result]
            print(f"從資料庫中找到 {len(stock_list)} 筆不重複的股票代碼。")
            return stock_list
        except Exception as e:
            print(f"從資料庫讀取股票列表時發生錯誤: {e}")
            return []

    def _get_latest_trade_date(self, stock_id):
        """
        從資料庫獲取特定股票的最新交易日期。
        如果資料庫中沒有該股票的數據，則返回 None。
        """
        if not self.engine:
            return None
        
        try:
            with self.engine.connect() as connection:
                query = text(f"SELECT MAX(TradeDate) FROM daily_prices WHERE StockID = :stock_id")
                result = connection.execute(query, {'stock_id': stock_id}).scalar()
                return result # result will be a datetime.date object or None
        except Exception as e:
            print(f"查詢 {stock_id} 最新交易日期時發生錯誤: {e}")
            return None

    def fetch_and_store_data(self, stock_list, end_date_str, is_initial_setup=True):
        if not self.engine:
            print("資料庫引擎未初始化，無法執行操作。")
            return

        table_name = 'daily_prices'
        total_stocks = len(stock_list)
        
        for i, stock_id in enumerate(stock_list):
            full_stock_id = f"{stock_id}.TW"
            print(f"\n正在處理第 {i+1}/{total_stocks} 筆: {full_stock_id}")

            # Determine start_date based on existing data or initial setup logic
            latest_db_date = self._get_latest_trade_date(stock_id)
            
            # If initial setup or no data in DB, fetch from 1 year ago.
            # Otherwise, fetch from the day after the latest DB date.
            if latest_db_date:
                # Add one day to the latest date from DB
                start_date = latest_db_date + timedelta(days=1)
                print(f"  資料庫中 {stock_id} 的最新日期為 {latest_db_date}，將從 {start_date} 開始更新。")
            else:
                # If no data in DB for this stock, fetch for the last year (or a reasonable initial period)
                start_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() - timedelta(days=365) # Default 1 year back
                print(f"  資料庫中無 {stock_id} 資料，將從 {start_date} 開始初始化。")

            start_date_str = start_date.strftime('%Y-%m-%d')

            # Ensure start_date is not in the future
            today = datetime.now().date()
            if start_date > today:
                print(f"  {stock_id} 的開始獲取日期 {start_date_str} 晚於今天，跳過獲取。")
                continue

            try:
                data = yf.download(full_stock_id, start=start_date_str, end=end_date_str)
                
                if data.empty or data[['Open', 'High', 'Low', 'Close', 'Volume']].isnull().all().all():
                    print(f"找不到 {full_stock_id} 的資料或資料為空，跳過此筆。")
                    continue

                # 檢查並扁平化 MultiIndex 欄位 (yfinance sometimes returns MultiIndex)
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0) # 修正為取第一層索引

                data.reset_index(inplace=True)
                data['StockID'] = stock_id
                data.rename(columns={
                    'Date': 'TradeDate', 'Open': 'OpenPrice', 'High': 'HighPrice',
                    'Low': 'LowPrice', 'Close': 'ClosePrice', 'Adj Close': 'AdjClosePrice', 'Volume': 'Volume'
                }, inplace=True)

                # 強制資料類型轉換，確保與資料庫欄位類型完全匹配
                data['StockID'] = data['StockID'].astype(str)
                data['TradeDate'] = pd.to_datetime(data['TradeDate']).dt.date

                # 確保所有預期的欄位都存在，即使是 NaN
                # 並明確選擇和排序欄位，以匹配資料庫結構
                final_columns = ['StockID', 'TradeDate', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'AdjClosePrice', 'Volume']
                for col in final_columns:
                    if col not in data.columns:
                        data[col] = pd.NA # 使用 pandas.NA 處理缺失值
                data = data[final_columns]
                
                print(f"準備寫入資料庫的欄位: {data.columns.tolist()}") # 新增診斷訊息
                print("--- DataFrame Head ---")
                print(data.head())
                print("--- DataFrame Info ---")
                data.info()
                print("----------------------")

                self._merge_data(table_name, data)
                
                print(f"成功處理 {full_stock_id} 的 {len(data)} 筆資料。")
                time.sleep(1) # Add a small delay to avoid overwhelming the API

            except Exception as e:
                print(f"處理 {full_stock_id} 時發生錯誤: {e}")

    def _merge_data(self, table_name, df):
        """使用 MERGE 語句來插入或更新資料 (優化為批次執行)"""
        if df.empty:
            return

        # Ensure TradeDate is formatted as 'YYYY-MM-DD' string for SQL parameter binding
        df['TradeDate'] = df['TradeDate'].astype(str) 

        merge_sql = text(f"""
        MERGE INTO {table_name} AS Target
        USING (SELECT :StockID AS StockID, :TradeDate AS TradeDate) AS Source
        ON Target.StockID = Source.StockID AND Target.TradeDate = Source.TradeDate
        WHEN MATCHED THEN
            UPDATE SET 
                OpenPrice = :OpenPrice, HighPrice = :HighPrice, LowPrice = :LowPrice,
                ClosePrice = :ClosePrice, AdjClosePrice = :AdjClosePrice, Volume = :Volume
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (StockID, TradeDate, OpenPrice, HighPrice, LowPrice, ClosePrice, AdjClosePrice, Volume)
            VALUES (:StockID, :TradeDate, :OpenPrice, :HighPrice, :LowPrice, :ClosePrice, :AdjClosePrice, :Volume);
        """)
        
        # 將 DataFrame 轉為 list of dicts，這是 SQLAlchemy 執行批次操作的標準格式
        params = df.to_dict('records')

        with self.engine.connect() as connection:
            # begin() 會開啟一個事務，確保所有操作都成功或都不成功
            with connection.begin():
                connection.execute(merge_sql, params)
        print(f"  成功執行 MERGE 操作，寫入 {len(df)} 筆資料。") # Added success print

    def initial_setup(self):
        """執行首次資料庫設定與資料匯入"""
        if not self.engine: return
        
        table_creation_query = text(f"""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='daily_prices' and xtype='U')
        CREATE TABLE daily_prices (
            StockID NVARCHAR(20) NOT NULL, TradeDate DATE NOT NULL, OpenPrice FLOAT, HighPrice FLOAT,
            LowPrice FLOAT, ClosePrice FLOAT, AdjClosePrice FLOAT, Volume BIGINT,
            PRIMARY KEY (StockID, TradeDate)
        );
        """)
        try:
            with self.engine.connect() as connection:
                connection.execute(table_creation_query)
                connection.commit()
            print("資料表 'daily_prices' 確認完畢。")
        except Exception as e:
            print(f"建立資料表時發生錯誤: {e}")
            return

        stock_list = self.get_stock_list_from_twse()
        if stock_list:
            # For initial setup, fetch data up to yesterday for all stocks.
            # The fetch_and_store_data will determine the actual start date for each stock.
            end_date = datetime.now().date() - timedelta(days=1) # Fetch up to yesterday
            self.fetch_and_store_data(stock_list, end_date.strftime('%Y-%m-%d'), is_initial_setup=True)

    def update_daily_data(self):
        """執行每日資料更新"""
        if not self.engine: return
        
        stock_list = self.get_stock_list_from_db() # Get all stocks that already have data
        if stock_list:
            # For daily update, fetch data up to yesterday.
            # The fetch_and_store_data will determine the actual start date for each stock.
            end_date = datetime.now().date() - timedelta(days=1) # Fetch up to yesterday
            print(f"\n開始從資料庫最新日期更新到 {end_date.strftime('%Y-%m-%d')} 的資料...")
            self.fetch_and_store_data(stock_list, end_date.strftime('%Y-%m-%d'), is_initial_setup=False)

print("Class 定義完成。")

if __name__ == '__main__':
    print("進入主程式區塊...")
    updater = DatabaseUpdater()
    
    # Check if database connection was successful
    if not updater.engine:
        print("資料庫連線失敗，無法執行任何操作。請檢查您的 config.ini 和資料庫服務。")
    else:
        print("請選擇要執行的操作：")
        print("1. 首次資料庫設定與大量資料匯入 (Initial Setup)")
        print("2. 每日資料更新 (Daily Update)")
        choice = input("請輸入選項 (1 或 2): ")

        if choice == '1':
            print("\n開始執行首次資料庫設定與大量資料匯入...")
            updater.initial_setup()
            print("\n首次資料匯入完成！")
        elif choice == '2':
            print("\n開始執行每日資料更新...")
            updater.update_daily_data()
            print("\n每日資料更新完成！")
        else:
            print("無效的選項。")