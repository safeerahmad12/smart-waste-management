from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class Bin(Base):
    __tablename__ = "bins"

    id = Column(Integer, primary_key=True, index=True)
    bin_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    location = Column(String, nullable=False)
    area = Column(String, nullable=False)
    fill_level = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="Empty")
    last_updated = Column(DateTime, default=datetime.utcnow)