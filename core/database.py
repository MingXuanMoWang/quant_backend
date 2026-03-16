from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 【注意】这里请替换成你真实的 PostgreSQL 账号密码和数据库名！
# 格式: postgresql://用户名:密码@主机地址:端口/数据库名
DATABASE_URL = "postgresql://ming:m5132735@49.232.242.55:5432/quant_db"

print(f"[Database] 正在连接数据库: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL, echo=False) # echo=True 可以打印所有SQL语句，需要时可开
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("[Database] 数据库连接引擎初始化成功！")
except Exception as e:
    print(f"[Database] 数据库连接失败: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()