from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
from datetime import datetime

class BacktestRecord(Base):
    __tablename__ = "backtest_records"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    strategy_name = Column(String)
    train_start = Column(DateTime)
    test_start = Column(DateTime)
    test_end = Column(DateTime)
    initial_cash = Column(Float)
    final_cash = Column(Float)
    total_return = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
class MarketSignal(Base):
    __tablename__ = "market_signals"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    signal = Column(Float)  # 1表示买入，0表示不操作
    updated_at = Column(DateTime, default=datetime.utcnow)