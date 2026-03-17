from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
import datetime # 关键修改：只导入模块

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
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
class MarketSignal(Base):
    __tablename__ = "market_signals"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    signal = Column(Float)  # 1表示买入，0表示不操作
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
class MarketVolatility(Base):
    __tablename__ = "market_volatility"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    middle_band = Column(Float)
    upper_band = Column(Float)
    lower_band = Column(Float)
    z_score = Column(Float)
    status = Column(String)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
# ================= 追加到 core/models.py 末尾 =================

class MarketMACD(Base):
    __tablename__ = "market_macd"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    dif = Column(Float)         # 快线
    dea = Column(Float)         # 慢线
    macd_hist = Column(Float)   # MACD柱状图 (动能)
    signal = Column(Float)      # 1为金叉(买入), 0为死叉(卖出)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class MarketRSI(Base):
    __tablename__ = "market_rsi"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    rsi_value = Column(Float)
    status = Column(String)     # 超买 / 超卖 / 正常
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class MarketKDJ(Base):
    __tablename__ = "market_kdj"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    k_value = Column(Float)
    d_value = Column(Float)
    j_value = Column(Float)
    signal = Column(Float)      # 1为金叉，0为死叉
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))