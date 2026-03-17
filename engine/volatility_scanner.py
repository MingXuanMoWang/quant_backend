import pandas as pd
import datetime # 关键修改：只导入模块
from data.provider import DataProvider
from strategy.bollinger import BollingerStrategy
from core.database import SessionLocal, engine, Base
from core.models import MarketVolatility

# 确保表结构存在
Base.metadata.create_all(bind=engine)


def run_volatility_scan(symbol_list):
    print(f"\n[Scanner] === 开始布林带波动率扫描 ===")
    db = SessionLocal()
    strategy = BollingerStrategy(window=20, num_std=2)

    for symbol in symbol_list:
        try:
            print(f"\n[Scanner] 处理股票: {symbol}")

            # 1. 获取数据
            df = DataProvider.get_stock_data(symbol, "2025-01-01", "2026-03-16")

            # 2. 策略计算
            analyzed_df = strategy.generate_signals(df)

            # 3. 日志检查计算结果
            latest = analyzed_df.iloc[-1]
            print(f"    - 最新价格: {latest['Close']:.2f}")
            print(f"    - 中轨: {latest['Middle']:.2f} | Std: {latest['Std']:.4f}")

            if pd.isna(latest['Middle']) or pd.isna(latest['Std']):
                print(f"    - ⚠️ 警告: 计算结果为 NaN，跳过该股。")
                continue

            # 4. 判定状态
            z = float(latest['Z_Score'])
            if z > 2:
                status = "超买"
            elif z < -2:
                status = "超卖"
            else:
                status = "正常"

            # 5. 更新数据库
            record = db.query(MarketVolatility).filter_by(symbol=symbol).first()
            if not record:
                record = MarketVolatility(symbol=symbol)
                db.add(record)

            record.price = float(latest['Close'])
            record.middle_band = float(latest['Middle'])
            record.upper_band = float(latest['Upper'])
            record.lower_band = float(latest['Lower'])
            record.z_score = z
            record.status = status

            # 【修复点】：使用 datetime.datetime.now(datetime.timezone.utc)
            # 解释：datetime 是模块，第一个 datetime 是模块里的类，now 是方法
            record.updated_at = datetime.datetime.now(datetime.timezone.utc)

            db.commit()
            print(f"    - 扫描结果: {status} | Z-Score: {z:.2f}")

        except Exception as e:
            db.rollback()
            print(f"    - ❌ 处理失败: {e}")

    db.close()
    print(f"\n[Scanner] === 全部扫描完成 ===")


if __name__ == "__main__":
    # 测试列表
    # stocks = ["601398", "600519", "000333"]
    stocks = [
        # 银行
        "601398", "601288", "601939", "601988", "600036", "600016", "601166", "601328",
        # 白酒与消费
        "600519", "000858", "600809", "603288", "600887", "000333",
        # 保险与金融
        "601318", "601628", "601601",
        # 石油、化工、能源
        "601857", "600028", "601088", "601888",
        # 科技、通信、半导体
        "600941", "601728", "601138", "600584", "002415", "002050",
        # 新能源、汽车、电力
        "601012", "601899", "600031", "002594", "601633", "600905",
        # 建筑、基建
        "601668", "601390", "601818",
        # 医药
        "600276", "600436", "000538",
        # 航空、物流、其他
        "600009", "601888", "601336", "601877", "600104", "000001", "600000",
        # 补充几个热门/市值大的
        "600019", "601985", "600030", "600010"
    ]
    run_volatility_scan(stocks)