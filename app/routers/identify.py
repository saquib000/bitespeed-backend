from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.contact import IdentifyRequest, IdentifyResponse
from app.services.identity_service import resolve_identity

router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse)
def identify(payload: IdentifyRequest, db: Session = Depends(get_db)):

    if not payload.email and not payload.phoneNumber:
        raise HTTPException(status_code=400, detail="At least one of email or phoneNumber is required")

    return resolve_identity(
        db=db,
        email=payload.email,
        phone=payload.phoneNumber
    )