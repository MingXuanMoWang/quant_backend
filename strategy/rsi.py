import pandas as pd
from .base import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, period=14, overbought=70, oversold=30):
        super().__init__("RSI (相对强弱指数)")
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

        # 计算每日涨跌幅
        delta = data['Close'].diff()

        # 分离上涨和下跌
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)

        # 使用指数移动平均(Wilder的平滑法可用alpha=1/period近似)
        avg_gain = gain.ewm(alpha=1/self.period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.period, adjust=False).mean()

        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))
        data['RSI'] = data['RSI'].fillna(50) # 初始值填50

        # 简单信号判定：RSI 低于超卖线产生买入信号
        data['Signal'] = 0.0
        data.loc[data['RSI'] < self.oversold, 'Signal'] = 1.0
        # 大于超买线也可以算作清仓信号0.0，默认就是0.0这里不用特意改

        return data