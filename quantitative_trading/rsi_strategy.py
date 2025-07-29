
import pandas as pd
import numpy as np
from strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) 策略。
    - 當 RSI 跌破超賣區 (例如 30) 時，產生買入訊號 (1)。
    - 當 RSI 突破超買區 (例如 70) 時，產生賣出訊號 (-1)。
    - 其他時間保持中立 (0)。
    """
    def __init__(self, data: pd.DataFrame, window: int = 14, overbought: int = 70, oversold: int = 30):
        super().__init__(data)
        self.window = window
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self) -> pd.DataFrame:
        signals = self.data.copy()

        # 計算 RSI
        delta = signals['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()

        rs = gain / loss
        signals['rsi'] = 100 - (100 / (1 + rs))

        # 產生訊號 (確保所有參與比較的都是一維 NumPy 陣列)
        rsi_arr = signals['rsi'].values.flatten()

        signal_arr = np.where(
            rsi_arr < self.oversold, # 買入條件
            1.0,
            np.where(
                rsi_arr > self.overbought, # 賣出條件
                -1.0,
                0.0 # 預設為 0
            )
        )
        signals['signal'] = signal_arr

        # 處理持倉變化 (確保所有參與比較的都是一維 NumPy 陣列)
        positions_arr = np.where(
            signal_arr == 1.0, 1.0,
            np.where(
                signal_arr == -1.0, -1.0,
                0.0
            )
        )
        signals['positions'] = positions_arr

        # 將參數儲存到 attrs 中
        signals.attrs['strategy_name'] = "RSI"
        signals.attrs['window'] = self.window
        signals.attrs['overbought'] = self.overbought
        signals.attrs['oversold'] = self.oversold

        return signals
