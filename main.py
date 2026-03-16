import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import pandas as pd

from core.database import engine, Base, get_db
from core.models import BacktestRecord
from data.provider import DataProvider
from strategy.sma_cross import SMACrossStrategy
from engine.backtester import BacktestEngine

print("\n[System] 正在初始化量化后台服务...")

# 初始化数据库表 (如果表不存在则创建)
try:
    Base.metadata.create_all(bind=engine)
    print("[System] 数据库表结构同步完成。")
except Exception as e:
    print(f"[System] 数据库表创建失败，请检查 PostgreSQL 是否已启动！错误信息: {e}")

app = FastAPI(title="量化回测框架 API")

# 允许 Vue 前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BacktestRequest(BaseModel):
    symbol: str
    train_start: str
    test_start: str
    test_end: str
    initial_cash: float


@app.post("/api/run_backtest")
def run_backtest(req: BacktestRequest, db: Session = Depends(get_db)):
    print("\n" + "=" * 50)
    print(f"[API] 收到前端回测请求: {req.model_dump()}")
    print("=" * 50)
    try:
        # 1. 获取数据
        df = DataProvider.get_stock_data(req.symbol, req.train_start, req.test_end)

        # 2. 初始化策略
        strategy = SMACrossStrategy(short_window=5, long_window=20)

        # 3. 运行引擎
        engine_instance = BacktestEngine(df, strategy, req.initial_cash)
        result = engine_instance.run(split_date=req.test_start)

        # 4. 保存数据库
        print("[API] 正在将回测记录保存至 PostgreSQL 数据库...")
        record = BacktestRecord(
            symbol=req.symbol,
            strategy_name=result['strategy'],
            # 将 pandas 的 Timestamp 转为原生 datetime
            train_start=pd.to_datetime(req.train_start).to_pydatetime(),
            test_start=pd.to_datetime(req.test_start).to_pydatetime(),
            test_end=pd.to_datetime(req.test_end).to_pydatetime(),
            # 确保资金和收益率为原生 float
            initial_cash=float(req.initial_cash),
            final_cash=float(result['final_cash']),
            total_return=float(result['total_return'])
        )
        db.add(record)
        db.commit()
        print("[API] 数据库保存成功！")

        return {"status": "success", "data": result}

    except Exception as e:
        print(f"\n[API] ❌ 执行发生错误: {str(e)}")
        return {"status": "error", "message": str(e)}


# ================= 关键修改在这里 =================
# 当你用 PyCharm 运行这个文件时，以下代码会启动一直监听的 Web 服务，不会 Exit code 0
if __name__ == "__main__":
    print("[System] 准备启动 Uvicorn Web 服务器，监听端口 8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)