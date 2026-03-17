import datetime
import pandas as pd
from data.provider import DataProvider
from strategy.macd import MACDStrategy
from core.database import SessionLocal, engine, Base
from core.models import MarketMACD

Base.metadata.create_all(bind=engine)

def run_macd_scan(symbol_list):
    print(f"\n[Scanner] === 开始 MACD 动能扫描 ===")
    db = SessionLocal()
    strategy = MACDStrategy()

    for symbol in symbol_list:
        try:
            df = DataProvider.get_stock_data(symbol, "2025-01-01", "2026-03-16")
            analyzed_df = strategy.generate_signals(df)
            latest = analyzed_df.iloc[-1]

            if pd.isna(latest['DIF']):
                continue

            record = db.query(MarketMACD).filter_by(symbol=symbol).first()
            if not record:
                record = MarketMACD(symbol=symbol)
                db.add(record)

            record.dif = float(latest['DIF'])
            record.dea = float(latest['DEA'])
            record.macd_hist = float(latest['MACD_Hist'])
            record.signal = float(latest['Signal'])
            record.updated_at = datetime.datetime.now(datetime.timezone.utc)

            db.commit()
            cross_status = "金叉 (多头)" if latest['Signal'] == 1.0 else "死叉 (空头)"
            print(f"[{symbol}] MACD 扫描成功 | 状态: {cross_status} | 柱状图: {latest['MACD_Hist']:.3f}")

        except Exception as e:
            db.rollback()
            print(f"[{symbol}] ❌ 处理失败: {e}")

    db.close()
    print(f"[Scanner] === MACD 扫描完成 ===\n")

if __name__ == "__main__":
    stocks =["601398", "600519", "000333", "002594", "600036"] # 可以替换为你的50只列表
    run_macd_scan(stocks)