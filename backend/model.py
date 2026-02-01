from sqlalchemy import Column, Integer, String
from database import Base


class BidCompany(Base):
    __tablename__ = "bid_company"

    bid_company = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, nullable=False)

    capability_level = Column(String(50), nullable=False)
    project_experience = Column(Integer, nullable=False) 
    certifications_held = Column(String(255))
    team_availability = Column(Integer)  
    domain_experience = Column(Integer)
    project_duration = Column(Integer)  
    deal_size_range = Column(String(100))
    types_worked_with = Column(String(255))