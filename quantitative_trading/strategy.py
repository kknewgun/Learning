import pandas as pd
import numpy as np

class BaseStrategy:
    """
    所有交易策略的基類。
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def generate_signals(self) -> pd.DataFrame:
        """
        生成交易訊號的抽象方法，子類必須實現。
        返回的 DataFrame 必須包含 'signal' 和 'positions' 欄位。
        """
        raise NotImplementedError("Subclasses must implement this method")


class MovingAverageCrossStrategy(BaseStrategy):
    """
    移動平均線 (MA) 交叉策略。
    - 當短期 MA 向上穿越長期 MA 時，產生買入訊號 (1)
    - 當短期 MA 向下穿越長期 MA 時，產生賣出訊號 (-1)
    - 其他時間保持中立 (0)
    """
    def __init__(self, data: pd.DataFrame, short_window: int, long_window: int):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self) -> pd.DataFrame:
        """
        根據 MA 交叉策略產生交易訊號，並將所有資訊整合到一個 DataFrame 中。

        Returns:
            pd.DataFrame: 包含價格、MA、訊號和部位變化的 DataFrame。
        """
        signals = self.data.copy()
        # 1. 計算移動平均線
        signals['short_ma'] = signals['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_ma'] = signals['Close'].rolling(window=self.long_window, min_periods=1).mean()

        # 2. 建立訊號 (當 short_ma > long_ma 時為持有，否則為空手)
        signals['signal'] = np.where(signals['short_ma'] > signals['long_ma'], 1.0, 0.0)

        # 3. 產生交易訂單 (訊號的變化)
        # .diff() 會計算目前訊號與前一筆訊號的差異
        # 買入訊號: signal 從 0 變成 1 (差異為 1)
        # 賣出訊號: signal 從 1 變成 0 (差異為 -1)
        signals['positions'] = signals['signal'].diff()

        # 將參數儲存到 attrs 中，方便後續使用
        signals.attrs['strategy_name'] = "移動平均線交叉 (MA Cross)"
        signals.attrs['short_window'] = self.short_window
        signals.attrs['long_window'] = self.long_window

        return signals