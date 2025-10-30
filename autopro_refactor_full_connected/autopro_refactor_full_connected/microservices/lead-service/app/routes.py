from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from autopro_common.db import async_session
from autopro_common.auth import verify_jwt_token
from .models import Lead

router = APIRouter()

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    status: str

    class Config:
        from_attributes = True

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/leads", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(verify_jwt_token)
):
    new_lead = Lead(**lead.dict())
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return new_lead

@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(verify_jwt_token)
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(verify_jwt_token)
):
    result = await db.execute(select(Lead).limit(100))
    leads = result.scalars().all()
    return leads
