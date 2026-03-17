import pandas as pd
from .base import BaseStrategy


class BollingerStrategy(BaseStrategy):
    def __init__(self, window=20, num_std=2):
        super().__init__("Bollinger_Bands (布林带)")
        self.window = window
        self.num_std = num_std

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        # 强制将 Close 转换为数值，非数值设为 NaN
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

        # 计算布林带
        data['Middle'] = data['Close'].rolling(window=self.window).mean()
        data['Std'] = data['Close'].rolling(window=self.window).std()
        data['Upper'] = data['Middle'] + (data['Std'] * self.num_std)
        data['Lower'] = data['Middle'] - (data['Std'] * self.num_std)

        # 计算 Z-Score，并处理分母为 0 的情况
        # 如果 Std 为 0，Z_Score 设为 0
        data['Z_Score'] = (data['Close'] - data['Middle']) / data['Std']
        data['Z_Score'] = data['Z_Score'].fillna(0)

        return data