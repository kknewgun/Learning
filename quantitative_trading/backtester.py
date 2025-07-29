import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Matplotlib 設定 ---
try:
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
except:
    print("Microsoft JhengHei font not found, using default font.")
plt.rcParams['axes.unicode_minus'] = False

class Backtester:
    def __init__(self, signals: pd.DataFrame, initial_capital: float):
        self.signals = signals
        self.initial_capital = initial_capital

    def run_backtest(self) -> pd.DataFrame:
        """
        執行回測，計算投資組合的每日價值。
        使用 .squeeze() 確保操作數為 Series，避免 DataFrame 廣播錯誤。
        """
        shares_to_trade = 100
        portfolio = pd.DataFrame(index=self.signals.index)

        # 確保 positions 是 Series
        positions = self.signals['positions'].shift(1).fillna(0).squeeze()
        portfolio['holdings'] = (positions.cumsum() * shares_to_trade).squeeze()

        # 確保所有操作數都是 Series
        holdings_series = portfolio['holdings'].squeeze()
        close_price_series = self.signals['Close'].squeeze()
        open_price_series = self.signals['Open'].squeeze()

        # 1. 計算股票市值
        portfolio['stock_value'] = (holdings_series * close_price_series).squeeze()

        # 2. 計算現金變化
        cash_change = - (positions.squeeze() * shares_to_trade * open_price_series).squeeze()
        portfolio['cash'] = (self.initial_capital + cash_change.cumsum()).squeeze()

        portfolio['total'] = (portfolio['cash'] + portfolio['stock_value']).squeeze()
        portfolio['returns'] = portfolio['total'].pct_change().squeeze()

        return portfolio.fillna(0)

    def evaluate_performance(self, portfolio: pd.DataFrame):
        if portfolio.empty or self.initial_capital == 0:
            print("Portfolio is empty or initial capital is zero, cannot evaluate performance.")
            return

        total_return = (portfolio['total'].iloc[-1] / self.initial_capital) - 1
        days = (portfolio.index[-1] - portfolio.index[0]).days
        annualized_return = (1 + total_return) ** (365.0 / days) - 1 if days > 0 else 0.0
        
        returns_std = portfolio['returns'].std()
        sharpe_ratio = np.sqrt(252) * (portfolio['returns'].mean() / returns_std) if returns_std != 0 else 0.0

        rolling_max = portfolio['total'].cummax()
        daily_drawdown = portfolio['total'] / rolling_max - 1.0
        max_drawdown = daily_drawdown.cummin().min()

        print("\n--- 回測績效 ---")
        print(f"初始資金:         {self.initial_capital:,.2f}")
        print(f"最終投資組合價值:   {portfolio['total'].iloc[-1]:,.2f}")
        print(f"總回報率:            {total_return:.2%}")
        print(f"年化回報率:       {annualized_return:,.2%}")
        print(f"夏普比率:            {sharpe_ratio:.2f}")
        print(f"最大回撤:        {max_drawdown:.2%}")

    def plot_performance(self, portfolio: pd.DataFrame):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True, gridspec_kw={'height_ratios': [1, 2]})
        stock_id = self.signals.attrs.get("stock_id", "Stock")
        strategy_name = self.signals.attrs.get("strategy_name", "Unknown Strategy")
        
        # 根據策略名稱設定主標題
        if strategy_name == "移動平均線交叉 (MA Cross)":
            short_window = self.signals.attrs.get("short_window", "N/A")
            long_window = self.signals.attrs.get("long_window", "N/A")
            fig.suptitle(f'回測績效: {stock_id} ({strategy_name} MA {short_window}/{long_window})')
        elif strategy_name == "Bollinger Bands":
            window = self.signals.attrs.get("window", "N/A")
            num_std_dev = self.signals.attrs.get("num_std_dev", "N/A")
            fig.suptitle(f'回測績效: {stock_id} ({strategy_name} {window}/{num_std_dev} 標準差)')
        elif strategy_name == "RSI":
            window = self.signals.attrs.get("window", "N/A")
            overbought = self.signals.attrs.get("overbought", "N/A")
            oversold = self.signals.attrs.get("oversold", "N/A")
            fig.suptitle(f'回測績效: {stock_id} ({strategy_name} {window} 超買:{overbought} 超賣:{oversold})')
        else:
            fig.suptitle(f'回測績效: {stock_id} ({strategy_name})')

        ax1.set_title('投資組合價值變化')
        portfolio['total'].plot(ax=ax1, label='總投資組合價值', color='b')
        ax1.set_ylabel("投資組合價值 (新台幣)")
        ax1.legend()
        ax1.grid(True)

        ax2.set_title('股價與交易信號')
        self.signals['Close'].plot(ax=ax2, label='收盤價', color='k', alpha=0.7)

        # 根據策略繪製不同的指標
        if strategy_name == "移動平均線交叉 (MA Cross)":
            short_window = self.signals.attrs.get("short_window", "N/A")
            long_window = self.signals.attrs.get("long_window", "N/A")
            self.signals['short_ma'].plot(ax=ax2, label=f'{short_window}日均線', linestyle='--')
            self.signals['long_ma'].plot(ax=ax2, label=f'{long_window}日均線', linestyle='--')
        elif strategy_name == "布林通道 (Bollinger Bands)":
            self.signals['rolling_mean'].plot(ax=ax2, label='移動平均線', linestyle='--', color='orange')
            self.signals['upper_band'].plot(ax=ax2, label='布林上軌', linestyle=':', color='red')
            self.signals['lower_band'].plot(ax=ax2, label='布林下軌', linestyle=':', color='green')
        elif strategy_name == "RSI":
            # RSI 通常會繪製在獨立的子圖中，這裡僅繪製價格和交易訊號
            # 如果需要繪製 RSI 指標本身，需要增加一個子圖
            pass # 不繪製 RSI 線，只顯示價格和交易訊號

        buy_signals = self.signals[self.signals.positions == 1.0]
        sell_signals = self.signals[self.signals.positions == -1.0]

        # 標示買入點
        if not buy_signals.empty:
            ax2.plot(buy_signals.index, self.signals['Close'].loc[buy_signals.index],
                     '^', markersize=12, color='g', lw=0, label='買入信號')

        # 標示賣出點
        if not sell_signals.empty:
            ax2.plot(sell_signals.index, self.signals['Close'].loc[sell_signals.index],
                     'v', markersize=12, color='r', lw=0, label='賣出信號')

        ax2.set_ylabel("股價 (新台幣)")
        ax2.legend()
        ax2.grid(True)

        plt.xlabel('Date')
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        return fig