import pandas as pd
import configparser
from sqlalchemy import create_engine, text
import urllib

class DataLoader:
    """
    負責從 MSSQL 資料庫讀取股價資料
    """
    def __init__(self, config_path='config.ini'):
        self.engine = self._create_db_engine(config_path)

    def _create_db_engine(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        db_config = config['Database']

        server = db_config['Server']
        database = db_config['Database']
        username = db_config['Username']
        password = db_config['Password']
        driver = db_config['Driver'].replace(' ', '+')

        encoded_password = urllib.parse.quote_plus(password)
        connection_string = f"mssql+pyodbc://{username}:{encoded_password}@{server}/{database}?driver={driver}"
        
        try:
            engine = create_engine(connection_string)
            return engine
        except Exception as e:
            print(f"資料庫連線失敗: {e}")
            return None

    def get_data(self, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
      
        if not self.engine:
            print("資料庫引擎未初始化，無法讀取資料。")
            return pd.DataFrame()

        # 移除 .TW 後綴 (如果有的話)
        stock_id_cleaned = stock_id.replace('.TW', '')

        query = text(f"""
            SELECT 
                TradeDate as [Date], 
                OpenPrice as [Open], 
                HighPrice as [High], 
                LowPrice as [Low], 
                ClosePrice as [Close], 
                Volume
            FROM 
                daily_prices
            WHERE 
                StockID = :stock_id AND 
                TradeDate BETWEEN :start_date AND :end_date
            ORDER BY 
                TradeDate ASC;
        """)

        try:
            with self.engine.connect() as connection:
                data = pd.read_sql(query, connection, params={
                    'stock_id': stock_id_cleaned,
                    'start_date': start_date,
                    'end_date': end_date
                })
            
            if data.empty:
                print(f"在資料庫中找不到 {stock_id_cleaned} 在指定期間的資料。")
                return pd.DataFrame()

            # 將 Date 欄位設定為索引，以符合既有程式的格式
            data.set_index('Date', inplace=True)
            return data
        except Exception as e:
            print(f"從資料庫讀取資料時發生錯誤: {e}")
            return pd.DataFrame()