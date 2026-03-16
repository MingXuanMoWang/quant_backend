import pandas as pd
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        print(f"[Strategy] 初始化策略基类: {self.name}")

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass