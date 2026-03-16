import yfinance as yf
import pandas as pd


class DataProvider:
    @staticmethod
    def get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        print(f"\n[Data Provider] 开始获取数据 | 股票: {symbol} | 区间: {start_date} 到 {end_date}")

        # 简单后缀处理
        if symbol.isdigit():
            sym = f"{symbol}.SS" if symbol.startswith(('6', '9')) else f"{symbol}.SZ"
        else:
            sym = symbol

        ticker = yf.Ticker(sym)
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            print(f"[Data Provider] 警告：未能获取到 {symbol} 的数据！")
            raise ValueError(f"无法获取 {symbol} 的数据，可能是节假日或代码错误")

        # 标准化处理
        df.reset_index(inplace=True)
        # 统一时区，去除时区信息方便比对
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        print(f"[Data Provider] 数据获取成功！共获取到 {len(df)} 条日线数据。")
        print(f"[Data Provider] 数据预览 (前3行):\n{df.head(3)}\n")

        return df