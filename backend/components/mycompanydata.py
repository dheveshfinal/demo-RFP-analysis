from fastapi import APIRouter,Request,Depends
from sqlalchemy.orm import Session
from database import get_db
from model import BidCompany


router=APIRouter()

@router.post("/mycompanydata")
async def mycompanydata(request:Request,db:Session=Depends(get_db)):
    data=await request.json()
    company = db.query(BidCompany).filter(
        BidCompany.bid_company == 1
    ).first()

    if company:
            company.capability_level = data.get("technicalCapability")
            company.project_experience = data.get("pastExperience")
            company.certifications_held = data.get("certifications")
            company.team_availability = data.get("teamAvailability")
            company.domain_experience = data.get("domainExperience")
            company.project_duration = data.get("maxDuration")
            company.deal_size_range = data.get("dealSizeRange")
            company.types_worked_with = data.get("clientType")
    else:
            company = BidCompany(
            bid_company=1,
            org_id=1,
            capability_level=data.get("technicalCapability"),
            project_experience=data.get("pastExperience"),
            certifications_held=data.get("certifications"),
            team_availability=data.get("teamAvailability"),
            domain_experience=data.get("domainExperience"),
            project_duration=data.get("maxDuration"),
            deal_size_range=data.get("dealSizeRange"),
            types_worked_with=data.get("clientType")
        )
    db.add(company)

    db.commit()
    return({
            "message":"data is inserted"
        }
        )