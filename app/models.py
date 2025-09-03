from sqlalchemy import Column, Integer, String, Float, DateTime, func
from .db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
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


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    sql = Column(String, nullable=True)
    tool = Column(String, nullable=True)
    result = Column(String, nullable=True)
    report = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def as_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "sql": self.sql,
            "tool": self.tool,
            "result": self.result,
            "report": self.report,
            "created_at": str(self.created_at) if self.created_at else None,
        }
