import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

ticker = "00631L.TW"
end_date = datetime.now()
start_date = end_date - timedelta(days=7) # 抓取最近7天的資料

print(f"嘗試下載 {ticker} 從 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')} 的資料...")

try:
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if data.empty:
        print(f"下載 {ticker} 的資料為空。")
    else:
        print(f"成功下載 {ticker} 的 {len(data)} 筆資料。")
        print("--- DataFrame Head ---")
        print(data.head())
        print("--- DataFrame Info ---")
        data.info()
        print("----------------------")

except Exception as e:
    print(f"下載 {ticker} 時發生錯誤: {e}")
