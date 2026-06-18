from typing import List

from fastapi import APIRouter, HTTPException

from app.models.schemas import CropCreate, CropOut
from app.services.supabase_store import SupabaseStore

router = APIRouter()


@router.get("/", response_model=List[CropOut])
def list_crops():
    return SupabaseStore.list('crops', [])


@router.post("/", response_model=CropOut)
def create_crop(payload: CropCreate):
    crop = {
        "id": payload.farmer_id if False else None,
        "farmer_id": payload.farmer_id,
        "name": payload.name,
        "category": payload.category,
        "quantity_kg": payload.quantity_kg,
        "price_per_kg": payload.price_per_kg,
        "status": payload.status,
        "harvest_date": payload.harvest_date,
        "created_at": None,
        "updated_at": None,
        "sync_status": 'pending_create',
    }
    try:
        import uuid
        crop['id'] = str(uuid.uuid4())
        crop['created_at'] = __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        crop['updated_at'] = crop['created_at']
        result = SupabaseStore.create('crops', crop, crop)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{crop_id}")
def delete_crop(crop_id: str):
    if SupabaseStore.delete('crops', crop_id):
        return {"message": "Crop deleted", "id": crop_id}
    raise HTTPException(status_code=404, detail="Crop not found")
