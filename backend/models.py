from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Enum options
regions = ("ANZ", "ASIA", "ME", "TA")
#statuses = ("Delivered", "NMI", "Returned")

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    comId = Column(String(50), unique=True, nullable=False)  # username
    password = Column(String(255), nullable=False)  # Later store hashed passwords
    programmer = Column(String(100), nullable=False)

    details = relationship('Detail', back_populates='user')

class Detail(Base):
    __tablename__ = 'detail'
    hmy = Column(Integer, primary_key=True, autoincrement=True)
    hsummary = Column(Integer, ForeignKey('summary.hmy'), nullable=True)
    date = Column(Date)
    userid = Column(Integer, ForeignKey('user.id'), nullable=False)
    region = Column(Enum(*regions))
    casenum = Column(Integer)
    #status = Column(Enum(*statuses), nullable=True)
    status = Column(String(50))
    comments = Column(String(255))
    summary = relationship("Summary", back_populates="detail")
    user = relationship('User', back_populates='details')

class Summary(Base):
    __tablename__ = 'summary'
    hmy = Column(Integer, primary_key=True)
    date = Column(Date)
    region = Column(String(255))
    existing = Column(Integer)
    assigned = Column(Integer)
    delivered = Column(Integer)
    returned = Column(Integer)
    resources = Column(Integer)
    unassigned = Column(Integer)
    pending = Column(Integer)

    detail = relationship("Detail", back_populates="summary")
