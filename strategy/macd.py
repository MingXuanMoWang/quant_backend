import pandas as pd
from .base import BaseStrategy


class MACDStrategy(BaseStrategy):
    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__("MACD (指数平滑异同移动平均线)")
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

        # 计算快线 EMA 和慢线 EMA
        ema_fast = data['Close'].ewm(span=self.fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=self.slow, adjust=False).mean()

        # 计算 DIF 和 DEA
        data['DIF'] = ema_fast - ema_slow
        data['DEA'] = data['DIF'].ewm(span=self.signal_period, adjust=False).mean()

        # 计算 MACD 柱 (有些地方是 (DIF-DEA)*2，这里取基础差值)
        data['MACD_Hist'] = (data['DIF'] - data['DEA']) * 2

        # 信号：DIF 大于 DEA 为金叉(多头)，否则死叉(空头)
        data['Signal'] = 0.0
        data.loc[data['DIF'] > data['DEA'], 'Signal'] = 1.0

        return data