import streamlit as st
import pandas as pd
import datetime

from data_loader import DataLoader
from strategy import MovingAverageCrossStrategy
from bollinger_bands_strategy import BollingerBandsStrategy
from rsi_strategy import RSIStrategy
from backtester import Backtester

# --- Streamlit UI --- 
st.set_page_config(layout="wide", page_title="台股量化交易回測平台")
st.title("台股量化交易回測平台")

# 側邊欄輸入參數
st.sidebar.header("回測參數設定")

stock_id = st.sidebar.text_input("股票代碼 (例如: 1101.TW)", "1101.TW")

start_date = st.sidebar.date_input("開始日期", datetime.date(2025, 1, 1))
end_date = st.sidebar.date_input("結束日期", datetime.date(2025, 12, 31))

# 策略選擇
strategy_name = st.sidebar.selectbox("選擇交易策略", 
                                     ["移動平均線交叉 (MA Cross)", 
                                      "布林通道 (Bollinger Bands)",
                                      "RSI (Relative Strength Index)"])

# 根據策略顯示不同參數
strategy_params = {}
if strategy_name == "移動平均線交叉 (MA Cross)":
    strategy_params["short_window"] = st.sidebar.slider("短期均線天數", 5, 60, 20)
    strategy_params["long_window"] = st.sidebar.slider("長期均線天數", 20, 200, 60)
elif strategy_name == "布林通道 (Bollinger Bands)":
    strategy_params["window"] = st.sidebar.slider("布林通道天數", 10, 50, 20)
    strategy_params["num_std_dev"] = st.sidebar.slider("標準差倍數", 1.0, 3.0, 2.0, 0.1)
elif strategy_name == "RSI (Relative Strength Index)":
    strategy_params["window"] = st.sidebar.slider("RSI 計算天數", 5, 30, 14)
    strategy_params["overbought"] = st.sidebar.slider("超買區 (例如: 70)", 60, 90, 70)
    strategy_params["oversold"] = st.sidebar.slider("超賣區 (例如: 30)", 10, 40, 30)

initial_capital = st.sidebar.number_input("初始資金", 100000.0, step=10000.0)

if st.sidebar.button("執行回測"):
    if not stock_id:
        st.sidebar.error("請輸入股票代碼！")
    else:
        st.subheader(f"回測結果: {stock_id}")
        
        # 1. 下載資料
        loader = DataLoader()
        data = loader.get_data(stock_id, str(start_date), str(end_date))

        if data.empty:
            st.error(f"無法下載 {stock_id} 的資料，請檢查股票代碼或日期範圍。")
        else:
            st.success(f"成功下載 {stock_id} 從 {start_date} 到 {end_date} 的股價資料，共 {len(data)} 筆。")

            # 2. 產生交易訊號
            strategy = None
            if strategy_name == "移動平均線交叉 (MA Cross)":
                strategy = MovingAverageCrossStrategy(data, 
                                                      strategy_params["short_window"],
                                                      strategy_params["long_window"])
            elif strategy_name == "布林通道 (Bollinger Bands)":
                strategy = BollingerBandsStrategy(data, 
                                                  strategy_params["window"],
                                                  strategy_params["num_std_dev"])
            elif strategy_name == "RSI (Relative Strength Index)":
                strategy = RSIStrategy(data, 
                                       strategy_params["window"],
                                       strategy_params["overbought"],
                                       strategy_params["oversold"])
            
            if strategy:
                signals = strategy.generate_signals()
                signals.attrs['stock_id'] = stock_id # 將股票 ID 加入 attrs
                st.info("交易訊號產生完成。")

                # 3. 執行回測
                backtester = Backtester(signals, initial_capital)
                portfolio = backtester.run_backtest()
                st.info("回測執行完成。")

                # 4. 顯示與評估結果
                st.subheader("回測績效")
                import io
                from contextlib import redirect_stdout

                f = io.StringIO()
                with redirect_stdout(f):
                    backtester.evaluate_performance(portfolio)
                performance_output = f.getvalue()
                st.text(performance_output)

                # 5. 視覺化
                st.subheader("績效圖表")
                fig = backtester.plot_performance(portfolio)
                st.pyplot(fig)
            else:
                st.error("未知的策略選擇！")