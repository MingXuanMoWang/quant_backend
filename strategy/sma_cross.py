import pandas as pd
from .base import BaseStrategy


class SMACrossStrategy(BaseStrategy):
    def __init__(self, short_window=5, long_window=20):
        super().__init__("SMA_Cross (双均线)")
        self.short_window = short_window
        self.long_window = long_window
        print(f"[Strategy] 策略参数已设置: 短期均线={self.short_window}, 长期均线={self.long_window}")

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        print("[Strategy] 开始计算技术指标和交易信号...")
        data = df.copy()

        # 1. 计算均线
        data['SMA_short'] = data['Close'].rolling(window=self.short_window).mean()
        data['SMA_long'] = data['Close'].rolling(window=self.long_window).mean()

        # 2. 生成信号 (短期大于长期，产生买入/持仓信号)
        data['Signal'] = 0.0
        data.loc[data['SMA_short'] > data['SMA_long'], 'Signal'] = 1.0

        print(f"[Strategy] 信号计算完成！总数据量: {len(data)}")
        return data