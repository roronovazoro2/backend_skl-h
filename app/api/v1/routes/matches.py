from fastapi import APIRouter

from app.services.match_service import MatchService

router = APIRouter()


@router.get("/job/{job_id}")
def match_workers(job_id: str):
    sample_job = {
        "id": job_id,
        "required_skill": "Harvesting",
        "location": "Sinnar Region",
        "payment": 1200,
    }
    workers = [
        {"id": "worker-1", "name": "Suresh Patil", "skills": ["Harvesting", "Sowing"], "daily_rate": 450},
        {"id": "worker-2", "name": "Amit Shinde", "skills": ["Tractor Driving"], "daily_rate": 650},
    ]
    return {"job_id": job_id, "matches": MatchService.build_match_scores(sample_job, workers)}
