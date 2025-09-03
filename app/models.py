from sqlalchemy import Column, Integer, String, Float
from .db import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)          # simplify: keep as string
    source = Column(String)        # "quickbooks" or "rootfi"
    type = Column(String)          # revenue/expense/profit
    category = Column(String)
    amount = Column(Float)

    def as_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "source": self.source,
            "type": self.type,
            "category": self.category,
            "amount": self.amount,
        }
