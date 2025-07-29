
import pandas as pd
import numpy as np
from strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    """
    布林通道 (Bollinger Bands) 策略。
    - 當收盤價跌破下軌時，產生買入訊號 (1)。
    - 當收盤價突破上軌時，產生賣出訊號 (-1)。
    - 其他時間保持中立 (0)。
    """
    def __init__(self, data: pd.DataFrame, window: int = 20, num_std_dev: float = 2.0):
        super().__init__(data)
        self.window = window
        self.num_std_dev = num_std_dev

    def generate_signals(self) -> pd.DataFrame:
        signals = self.data.copy()

        # 計算布林通道
        signals['rolling_mean'] = signals['Close'].rolling(window=self.window).mean()
        signals['rolling_std'] = signals['Close'].rolling(window=self.window).std()
        signals['upper_band'] = signals['rolling_mean'] + (signals['rolling_std'] * self.num_std_dev)
        signals['lower_band'] = signals['rolling_mean'] - (signals['rolling_std'] * self.num_std_dev)

        # 產生訊號 (確保所有參與比較的都是一維 NumPy 陣列)
        close_arr = signals['Close'].values.flatten()
        lower_band_arr = signals['lower_band'].values.flatten()
        upper_band_arr = signals['upper_band'].values.flatten()

        signal_arr = np.where(
            close_arr < lower_band_arr, # 買入條件
            1.0,
            np.where(
                close_arr > upper_band_arr, # 賣出條件
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
        signals.attrs['strategy_name'] = "Bollinger Bands"
        signals.attrs['window'] = self.window
        signals.attrs['num_std_dev'] = self.num_std_dev

        return signals
