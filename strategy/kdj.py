import pandas as pd
from .base import BaseStrategy

class KDJStrategy(BaseStrategy):
    def __init__(self, n=9, m1=3, m2=3):
        super().__init__("KDJ (随机指标)")
        self.n = n
        self.m1 = m1
        self.m2 = m2

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        data['High'] = pd.to_numeric(data['High'], errors='coerce')
        data['Low'] = pd.to_numeric(data['Low'], errors='coerce')

        # 1. 计算 N 日内的最低价和最高价
        low_min = data['Low'].rolling(window=self.n, min_periods=1).min()
        high_max = data['High'].rolling(window=self.n, min_periods=1).max()

        # 2. 计算 RSV (未成熟随机值)
        # 防止分母为0
        denominator = high_max - low_min
        denominator = denominator.replace(0, 1e-10)
        rsv = (data['Close'] - low_min) / denominator * 100

        # 3. 计算 K, D, J (使用平滑移动平均，国内常用 alpha=1/m)
        data['K'] = rsv.ewm(alpha=1/self.m1, adjust=False).mean()
        data['D'] = data['K'].ewm(alpha=1/self.m2, adjust=False).mean()
        data['J'] = 3 * data['K'] - 2 * data['D']

        # 信号：K > D 金叉买入/持仓
        data['Signal'] = 0.0
        data.loc[data['K'] > data['D'], 'Signal'] = 1.0

        return data