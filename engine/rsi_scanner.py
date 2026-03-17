import datetime
import pandas as pd
from data.provider import DataProvider
from strategy.rsi import RSIStrategy
from core.database import SessionLocal, engine, Base
from core.models import MarketRSI

Base.metadata.create_all(bind=engine)

def run_rsi_scan(symbol_list):
    print(f"\n[Scanner] === 开始 RSI 超买超卖扫描 ===")
    db = SessionLocal()
    strategy = RSIStrategy()

    for symbol in symbol_list:
        try:
            df = DataProvider.get_stock_data(symbol, "2025-01-01", "2026-03-16")
            analyzed_df = strategy.generate_signals(df)
            latest = analyzed_df.iloc[-1]

            rsi_val = float(latest['RSI'])
            if pd.isna(rsi_val):
                continue

            if rsi_val >= 70:
                status = "超买 (风险高)"
            elif rsi_val <= 30:
                status = "超卖 (可建仓)"
            else:
                status = "正常"

            record = db.query(MarketRSI).filter_by(symbol=symbol).first()
            if not record:
                record = MarketRSI(symbol=symbol)
                db.add(record)

            record.rsi_value = rsi_val
            record.status = status
            record.updated_at = datetime.datetime.now(datetime.timezone.utc)

            db.commit()
            print(f"[{symbol}] RSI 扫描成功 | RSI值: {rsi_val:.2f} | 状态: {status}")

        except Exception as e:
            db.rollback()
            print(f"[{symbol}] ❌ 处理失败: {e}")

    db.close()
    print(f"[Scanner] === RSI 扫描完成 ===\n")

if __name__ == "__main__":
    stocks =["601398", "600519", "000333", "002594", "600036"] # 替换为你的列表
    run_rsi_scan(stocks)