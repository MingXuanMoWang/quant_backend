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