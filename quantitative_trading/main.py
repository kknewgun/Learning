
import pandas as pd
from data_loader import DataLoader
from strategy import MovingAverageCrossStrategy
from backtester import Backtester

if __name__ == "__main__":
    # --- 參數設定 ---
    stock_id = "2330.TW"  # 台積電
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    short_window = 20  # 短期移動平均線
    long_window = 60   # 長期移動平均線
    initial_capital = 1000000.0 # 初始資金

    # 1. 下載資料
    loader = DataLoader()
    data = loader.get_data(stock_id, start_date, end_date)
    print(f"成功下載 {stock_id} 從 {start_date} 到 {end_date} 的股價資料，共 {len(data)} 筆。")


    # 2. 產生交易訊號
    print("Generating trading signals...")
    strategy = MovingAverageCrossStrategy(data, short_window, long_window)
    signals = strategy.generate_signals()
    signals.attrs['stock_id'] = stock_id # 將股票 ID 加入 attrs
    print("Trading signals generated.")

    # 3. 執行回測
    print("Running backtest...")
    # 注意：現在 Backtester 只接收 signals 和 initial_capital
    backtester = Backtester(signals, initial_capital)
    portfolio = backtester.run_backtest()
    print("Backtest completed.")

    # 4. 顯示與評估結果
    backtester.evaluate_performance(portfolio)

    # 5. 視覺化
    print("Plotting performance...")
    backtester.plot_performance(portfolio)
