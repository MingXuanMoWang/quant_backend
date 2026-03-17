import datetime
import pandas as pd
from data.provider import DataProvider
from strategy.kdj import KDJStrategy
from core.database import SessionLocal, engine, Base
from core.models import MarketKDJ

Base.metadata.create_all(bind=engine)

def run_kdj_scan(symbol_list):
    print(f"\n[Scanner] === 开始 KDJ 随机指标扫描 ===")
    db = SessionLocal()
    strategy = KDJStrategy()

    for symbol in symbol_list:
        try:
            df = DataProvider.get_stock_data(symbol, "2025-01-01", "2026-03-16")
            analyzed_df = strategy.generate_signals(df)
            latest = analyzed_df.iloc[-1]

            if pd.isna(latest['K']):
                continue

            record = db.query(MarketKDJ).filter_by(symbol=symbol).first()
            if not record:
                record = MarketKDJ(symbol=symbol)
                db.add(record)

            record.k_value = float(latest['K'])
            record.d_value = float(latest['D'])
            record.j_value = float(latest['J'])
            record.signal = float(latest['Signal'])
            record.updated_at = datetime.datetime.now(datetime.timezone.utc)

            db.commit()
            cross_status = "金叉 (偏多)" if latest['Signal'] == 1.0 else "死叉 (偏空)"
            print(f"[{symbol}] KDJ 扫描成功 | 状态: {cross_status} | K: {latest['K']:.1f}, D: {latest['D']:.1f}, J: {latest['J']:.1f}")

        except Exception as e:
            db.rollback()
            print(f"[{symbol}] ❌ 处理失败: {e}")

    db.close()
    print(f"[Scanner] === KDJ 扫描完成 ===\n")

if __name__ == "__main__":
    stocks =["601398", "600519", "000333", "002594", "600036"] # 替换为你的列表
    run_kdj_scan(stocks)