from typing import List

from fastapi import APIRouter, HTTPException

from app.models.schemas import JobCreate, JobOut
from app.services.supabase_store import SupabaseStore

router = APIRouter()


@router.get("/", response_model=List[JobOut])
def list_jobs():
    return SupabaseStore.list('jobs', [])


@router.post("/", response_model=JobOut)
def create_job(payload: JobCreate):
    import datetime
    import uuid
    job = {
        "id": str(uuid.uuid4()),
        "farmer_id": "e3cb89cf-4a3b-4861-84bb-7313a0c5c3fb",
        "worker_id": payload.worker_id,
        "title": payload.title,
        "description": payload.description,
        "location": payload.location,
        "payment": payload.payment,
        "required_skill": payload.required_skill,
        "status": payload.status,
        "created_at": datetime.datetime.utcnow().isoformat() + 'Z',
        "updated_at": datetime.datetime.utcnow().isoformat() + 'Z',
        "sync_status": 'pending_create',
    }
    try:
        return SupabaseStore.create('jobs', job, job)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{job_id}/assign")
def assign_worker(job_id: str, worker_id: str):
    updated = SupabaseStore.update('jobs', job_id, {"worker_id": worker_id, "status": 'assigned'})
    if updated is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Worker assigned", "job_id": job_id, "worker_id": worker_id}


@router.delete("/{job_id}/unassign")
def unassign_worker(job_id: str):
    updated = SupabaseStore.update('jobs', job_id, {"worker_id": None, "status": 'open'})
    if updated is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Worker unassigned", "job_id": job_id}


@router.delete("/{job_id}")
def delete_job(job_id: str):
    if SupabaseStore.delete('jobs', job_id):
        return {"message": "Job deleted", "id": job_id}
    raise HTTPException(status_code=404, detail="Job not found")
