import datetime

from data.provider import DataProvider
from strategy.sma_cross import SMACrossStrategy
from core.database import SessionLocal
from core.models import MarketSignal

from core.database import engine, Base
from core.models import MarketSignal

# 在开始扫描前，强制执行一次同步
print("[System] 正在同步数据库表结构...")
Base.metadata.create_all(bind=engine)
print("[System] 表结构同步检查完毕。")
def run_market_scan(symbol_list):
    # 这里直接创建连接，但在循环内处理每一个股票的事务
    db = SessionLocal()
    strategy = SMACrossStrategy()

    for symbol in symbol_list:
        try:
            # 1. 获取数据
            df = DataProvider.get_stock_data(symbol, "2025-01-01", "2026-03-16")
            analyzed_df = strategy.generate_signals(df)
            latest_signal = float(analyzed_df.iloc[-1]['Signal'])

            # 2. 查询并更新
            existing = db.query(MarketSignal).filter_by(symbol=symbol).first()
            if existing:
                existing.signal = latest_signal
                existing.updated_at = datetime.utcnow()
            else:
                new_record = MarketSignal(symbol=symbol, signal=latest_signal)
                db.add(new_record)

            # 3. 成功则提交
            db.commit()
            print(f"股票 {symbol} 扫描成功，信号: {latest_signal}")

        except Exception as e:
            # 【关键点】一旦出错，立刻回滚当前事务，清理连接状态！
            db.rollback()
            print(f"股票 {symbol} 处理失败: {e}")
            # 注意：这里不需要关闭 db，继续下一次循环即可

    db.close()


# 你只需要在这里运行它
if __name__ == "__main__":
    # 核心大盘股与各行业龙头列表 (共50只)
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
    run_market_scan(stocks)