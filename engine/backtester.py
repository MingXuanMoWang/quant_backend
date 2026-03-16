import pandas as pd
from strategy.base import BaseStrategy


class BacktestEngine:
    def __init__(self, data: pd.DataFrame, strategy: BaseStrategy, initial_cash: float = 100000.0):
        self.data = data
        self.strategy = strategy
        self.initial_cash = initial_cash
        print(f"[Engine] 回测引擎初始化 | 初始资金: ¥{self.initial_cash}")

    def run(self, split_date: str):
        print(f"\n[Engine] --- 开始执行回测 ---")
        print(f"[Engine] 分析预热期: {self.data['Date'].iloc[0].strftime('%Y-%m-%d')} 到 {split_date}")
        print(f"[Engine] 真实测试对比期: 从 {split_date} 开始")

        # 1. 策略全局计算信号
        analyzed_data = self.strategy.generate_signals(self.data)

        # 2. 截取测试期 (Out-of-Sample)
        test_data = analyzed_data[analyzed_data['Date'] >= pd.to_datetime(split_date)].copy()

        if test_data.empty:
            print("[Engine] 错误：测试期切割后无数据！")
            raise ValueError(f"分界日期 {split_date} 之后没有数据，请检查日期设置！")

        print(f"[Engine] 测试期数据截取成功，共有 {len(test_data)} 个交易日用于真实回测。")

        # 3. 向量化计算回测收益
        test_data['Position'] = test_data['Signal'].shift(1).fillna(0)
        test_data['Daily_Return'] = test_data['Close'].pct_change().fillna(0)
        test_data['Strategy_Return'] = test_data['Daily_Return'] * test_data['Position']
        test_data['Cumulative_Return'] = (1 + test_data['Strategy_Return']).cumprod()
        test_data['Portfolio_Value'] = self.initial_cash * test_data['Cumulative_Return']

        # 4. 提取结果
        final_cash = float(test_data['Portfolio_Value'].iloc[-1])
        total_return = float((final_cash - self.initial_cash) / self.initial_cash)

        print(f"[Engine] 回测完成！期末资金: ¥{final_cash:.2f} | 总收益率: {total_return * 100:.2f}%")

        # 处理图表数据时，如果图表也报错，可以确保里面的内容也是原生类型
        # 不过目前 FastAPI 的 JSON 序列化器通常能搞定这里，主要改上面的 final_cash 即可
        chart_data = test_data[['Date', 'Close', 'Portfolio_Value', 'Signal']].to_dict('records')

        return {
            "strategy": self.strategy.name,
            "initial_cash": float(self.initial_cash),
            "final_cash": round(final_cash, 2),
            "total_return": round(total_return, 4),
            "chart_data": chart_data
        }