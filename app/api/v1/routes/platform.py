import datetime as dt
import hashlib
import uuid
from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.supabase_store import SupabaseStore

router = APIRouter()


def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    clean = {k: v for k, v in user.items() if k != "password_hash"}
    clean["skills"] = clean.get("skills") or []
    return clean


def days_between(start_date: str, end_date: str) -> int:
    try:
        start = dt.date.fromisoformat(start_date)
        end = dt.date.fromisoformat(end_date)
        return max(1, (end - start).days + 1)
    except ValueError:
        return 1


def state() -> Dict[str, List[Dict[str, Any]]]:
    return APP_STATE


class LoginPayload(BaseModel):
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class RegisterPayload(BaseModel):
    role: str
    email: str
    password: str
    full_name: str
    phone: str
    state: str = "Maharashtra"
    buyer_type: Optional[str] = None
    preferences: Optional[List[str]] = None
    skills: List[str] = []
    daily_rate: Optional[float] = None
    experience_yrs: Optional[int] = None


class ListingPayload(BaseModel):
    farmer_id: str
    name: str
    category: str
    quantity_kg: float
    price_per_kg: float
    location: str
    description: Optional[str] = None
    status: str = "active"


class InquiryPayload(BaseModel):
    buyer_id: str
    farmer_id: str
    listing_id: str
    message: Optional[str] = None


class InquiryStatusPayload(BaseModel):
    status: str


class AdvisoryPayload(BaseModel):
    farmer_id: str
    input_type: Literal["image", "voice", "text"]
    input_reference: Optional[str] = None
    description: Optional[str] = None
    language: str = "en-IN"


class DraftListingPayload(BaseModel):
    farmer_id: str
    name: str
    category: str
    quantity_kg: float
    price_per_kg: float
    location: str
    description: Optional[str] = None
    status: str = "draft"


class AIDraftPayload(BaseModel):
    text: Optional[str] = None
    voice_transcript: Optional[str] = None
    location_hint: Optional[str] = None
    category_hint: Optional[str] = None


class EquipmentPayload(BaseModel):
    owner_id: str
    name: str
    category: str
    description: str = ""
    daily_rate: float
    location: str
    available: bool = True


class RentalPayload(BaseModel):
    equipment_id: str
    renter_id: str
    start_date: str
    end_date: str
    message: str = ""


class RentalStatusPayload(BaseModel):
    status: str


class JobPayload(BaseModel):
    farmer_id: str
    title: str
    description: str
    location: str
    required_skill: str
    daily_wage: float
    planned_days: int = 1
    start_date: str
    assigned_tasks: List[str] = Field(default_factory=list)


class ApplicationPayload(BaseModel):
    job_id: str
    laborer_id: str
    message: str = ""


class ApplicationStatusPayload(BaseModel):
    status: str


class LaborEngagementPayload(BaseModel):
    farmer_id: str
    worker_id: str
    job_id: str
    cost_per_laborer: float
    working_days: int
    duration: str
    assigned_tasks: List[str] = Field(default_factory=list)
    status: str = "ACTIVE"


class WorkdayPayload(BaseModel):
    job_id: str
    laborer_id: str
    date: str
    present: bool = True
    note: str = ""


class VerificationPayload(BaseModel):
    status: str
    admin_note: str = ""


class BlacklistPayload(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    reason: str


class VoiceSessionPayload(BaseModel):
    user_id: Optional[str] = None
    session_id: str
    transcript: str
    language: str = "en-IN"
    translated_text: Optional[str] = None
    source: str = "intern4-ai-transcriber"
    metadata: Dict[str, Any] = {}


def seed_state() -> Dict[str, List[Dict[str, Any]]]:
    current = now_iso()
    admin = {
        "id": "user_admin",
        "email": "admin@kissan.in",
        "password_hash": hash_password("admin123"),
        "full_name": "Platform Admin",
        "phone": "+91 90000 00000",
        "role": "ADMIN",
        "state": None,
        "skills": [],
        "daily_rate": None,
        "experience_yrs": None,
        "status": "APPROVED",
        "blacklist_reason": None,
        "admin_note": "Internal administrator",
        "created_at": current,
        "updated_at": current,
    }
    farmer = {
        "id": "user_farmer_ramesh",
        "email": "ramesh@kissan.in",
        "password_hash": hash_password("farmer123"),
        "full_name": "Ramesh Patil",
        "phone": "+91 91234 56789",
        "role": "FARMER",
        "state": "Maharashtra",
        "skills": [],
        "daily_rate": None,
        "experience_yrs": None,
        "status": "APPROVED",
        "blacklist_reason": None,
        "admin_note": "Land records and phone verified.",
        "created_at": current,
        "updated_at": current,
    }
    farmer2 = {
        "id": "user_farmer_anita",
        "email": "anita@kissan.in",
        "password_hash": hash_password("farmer123"),
        "full_name": "Anita Kaur",
        "phone": "+91 98765 43210",
        "role": "FARMER",
        "state": "Punjab",
        "skills": [],
        "daily_rate": None,
        "experience_yrs": None,
        "status": "APPROVED",
        "blacklist_reason": None,
        "admin_note": "Approved farmer.",
        "created_at": current,
        "updated_at": current,
    }
    buyer = {
        "id": "user_buyer_vijay",
        "email": "vijay@kissan.in",
        "password_hash": hash_password("buyer123"),
        "full_name": "Vijay Traders",
        "phone": "+91 93333 44444",
        "role": "BUYER",
        "buyer_type": "trader",
        "state": "Maharashtra",
        "preferences": ["Wheat", "Rice"],
        "status": "APPROVED",
        "blacklist_reason": None,
        "admin_note": "Verified buyer profile.",
        "created_at": current,
        "updated_at": current,
    }
    laborer = {
        "id": "user_labor_suresh",
        "email": "suresh@kissan.in",
        "password_hash": hash_password("labor123"),
        "full_name": "Suresh Shinde",
        "phone": "+91 91111 11111",
        "role": "LABORER",
        "state": "Maharashtra",
        "skills": ["Harvesting", "Sowing"],
        "daily_rate": 450,
        "experience_yrs": 6,
        "status": "APPROVED",
        "blacklist_reason": None,
        "admin_note": "Identity verified.",
        "created_at": current,
        "updated_at": current,
    }
    laborer2 = {
        "id": "user_labor_amit",
        "email": "amit@kissan.in",
        "password_hash": hash_password("labor123"),
        "full_name": "Amit Pawar",
        "phone": "+91 92222 22222",
        "role": "LABORER",
        "state": "Maharashtra",
        "skills": ["Tractor Driving", "Soil Tilling"],
        "daily_rate": 650,
        "experience_yrs": 4,
        "status": "APPROVED",
        "blacklist_reason": None,
        "admin_note": "Approved worker.",
        "created_at": current,
        "updated_at": current,
    }
    pending_labor = {
        "id": "user_labor_priya",
        "email": "priya@kissan.in",
        "password_hash": hash_password("labor123"),
        "full_name": "Priya Verma",
        "phone": "+91 93333 33333",
        "role": "LABORER",
        "state": "Punjab",
        "skills": ["Weeding", "Irrigation"],
        "daily_rate": 380,
        "experience_yrs": 2,
        "status": "PENDING",
        "blacklist_reason": None,
        "admin_note": "Awaiting admin verification.",
        "created_at": current,
        "updated_at": current,
    }
    equipment = [
        {
            "id": "eq_tractor_575",
            "owner_id": farmer["id"],
            "name": "Mahindra Tractor 575 DI",
            "category": "Tractor",
            "description": "47 HP tractor with trolley. Ideal for tilling and haulage.",
            "daily_rate": 1800,
            "available": True,
            "location": "Nashik, Maharashtra",
            "created_at": current,
            "updated_at": current,
        },
        {
            "id": "eq_rotavator",
            "owner_id": farmer["id"],
            "name": "Rotavator (6 feet)",
            "category": "Tillage",
            "description": "Heavy-duty rotavator for seedbed preparation.",
            "daily_rate": 700,
            "available": True,
            "location": "Nashik, Maharashtra",
            "created_at": current,
            "updated_at": current,
        },
        {
            "id": "eq_thresher",
            "owner_id": farmer["id"],
            "name": "Thresher Machine",
            "category": "Thresher",
            "description": "Multi-crop thresher, tractor driven.",
            "daily_rate": 1200,
            "available": False,
            "location": "Sinnar, Maharashtra",
            "created_at": current,
            "updated_at": current,
        },
        {
            "id": "eq_harvester",
            "owner_id": farmer2["id"],
            "name": "Combine Harvester",
            "category": "Harvester",
            "description": "Self-propelled combine harvester for wheat and paddy.",
            "daily_rate": 6500,
            "available": True,
            "location": "Ludhiana, Punjab",
            "created_at": current,
            "updated_at": current,
        },
    ]
    jobs = [
        {
            "id": "job_wheat",
            "farmer_id": farmer["id"],
            "laborer_id": None,
            "title": "Wheat Harvesting - 4 acres",
            "description": "Manual and machine harvesting of wheat over 4 acres near Sinnar. Lunch provided.",
            "location": "Sinnar, Maharashtra",
            "required_skill": "Harvesting",
            "daily_wage": 550,
            "planned_days": 3,
            "start_date": "2026-06-19",
            "status": "OPEN",
            "created_at": current,
            "updated_at": current,
        },
        {
            "id": "job_sugarcane",
            "farmer_id": farmer["id"],
            "laborer_id": laborer["id"],
            "title": "Sugarcane Loading Labor",
            "description": "Loading harvested sugarcane onto trucks. Heavy work, daily wage paid same day.",
            "location": "Nashik, Maharashtra",
            "required_skill": "Weeding",
            "daily_wage": 480,
            "planned_days": 5,
            "start_date": "2026-06-22",
            "status": "ASSIGNED",
            "created_at": current,
            "updated_at": current,
        },
    ]
    applications = [
        {
            "id": "app_suresh_sugarcane",
            "job_id": "job_sugarcane",
            "laborer_id": laborer["id"],
            "status": "ACCEPTED",
            "message": "I can start this week.",
            "created_at": current,
        },
        {
            "id": "app_priya_paddy",
            "job_id": "job_wheat",
            "laborer_id": pending_labor["id"],
            "status": "PENDING",
            "message": "Experienced in harvesting and field work.",
            "created_at": current,
        },
    ]
    rentals = [
        {
            "id": "rent_thresher",
            "equipment_id": "eq_thresher",
            "renter_id": farmer2["id"],
            "owner_id": farmer["id"],
            "status": "ACCEPTED",
            "start_date": "2026-06-17",
            "end_date": "2026-06-17",
            "days": 1,
            "total_cost": 1200,
            "message": "Need it for one day.",
            "created_at": current,
            "updated_at": current,
        }
    ]
    engagements = [
        {
            "id": "eng_sugarcane",
            "farmer_id": farmer["id"],
            "worker_id": laborer["id"],
            "job_id": "job_sugarcane",
            "cost_per_laborer": 480,
            "working_days": 3,
            "duration": "3 days",
            "assigned_tasks": ["Loading harvested cane", "Stacking bundles"],
            "status": "ACTIVE",
            "total_cost": 1440,
            "created_at": current,
            "updated_at": current,
        }
    ]
    notifications = [
        {
            "id": "note_job_application",
            "user_id": farmer["id"],
            "type": "JOB_APPLICATION",
            "title": "New job application",
            "message": "Priya Verma applied for Wheat Harvesting - 4 acres.",
            "read": False,
            "link": "labor-hiring",
            "created_at": current,
        },
        {
            "id": "note_rental_request",
            "user_id": farmer["id"],
            "type": "RENTAL_REQUEST",
            "title": "New rental request",
            "message": "Anita Kaur requested to rent Thresher Machine.",
            "read": False,
            "link": "my-rentals",
            "created_at": current,
        },
        {
            "id": "note_inquiry_received",
            "user_id": farmer["id"],
            "type": "INQUIRY_RECEIVED",
            "title": "New buyer inquiry",
            "message": "Vijay Traders asked about Fresh Wheat.",
            "read": False,
            "link": "marketplace-inquiries",
            "created_at": current,
        },
        {
            "id": "note_labor_assigned",
            "user_id": laborer["id"],
            "type": "JOB_ASSIGNED",
            "title": "Application accepted",
            "message": "Ramesh Patil accepted your application for Sugarcane Loading Labor.",
            "read": False,
            "link": "my-job",
            "created_at": current,
        },
    ]
    listings = [
        {
            "id": "list_wheat_01",
            "farmer_id": farmer["id"],
            "name": "Fresh Wheat",
            "category": "Grain",
            "quantity_kg": 2000,
            "price_per_kg": 24.0,
            "location": "Sinnar, Maharashtra",
            "description": "Premium quality wheat, freshly harvested.",
            "status": "active",
            "created_at": current,
            "updated_at": current,
        },
        {
            "id": "list_rice_01",
            "farmer_id": farmer2["id"],
            "name": "Organic Rice",
            "category": "Grain",
            "quantity_kg": 1200,
            "price_per_kg": 38.5,
            "location": "Ludhiana, Punjab",
            "description": "Organic paddy rice delivered dry.",
            "status": "active",
            "created_at": current,
            "updated_at": current,
        },
    ]
    inquiries = [
        {
            "id": "inq_01",
            "buyer_id": buyer["id"],
            "farmer_id": farmer["id"],
            "listing_id": "list_wheat_01",
            "message": "Interested in 500 kg, please confirm availability.",
            "status": "pending",
            "created_at": current,
            "updated_at": current,
        }
    ]
    advisories = [
        {
            "id": "adv_01",
            "farmer_id": farmer["id"],
            "input_type": "text",
            "input_reference": None,
            "description": "Leaf spots and yellowing on wheat plants.",
            "language": "en-IN",
            "diagnosis": "Fungal infection",
            "probability": 0.72,
            "recommendation": "Apply a copper-based fungicide and improve drainage.",
            "created_at": current,
            "updated_at": current,
        }
    ]
    draft_listings = [
        {
            "id": "draft_01",
            "farmer_id": farmer["id"],
            "name": "Draft Mustard Seeds",
            "category": "Oilseed",
            "quantity_kg": 300,
            "price_per_kg": 55.0,
            "location": "Sinnar, Maharashtra",
            "description": "Awaiting confirmation on moisture content.",
            "status": "draft",
            "created_at": current,
            "updated_at": current,
        }
    ]
    return {
        "users": [admin, farmer, farmer2, buyer, laborer, laborer2, pending_labor],
        "equipment": equipment,
        "rentals": rentals,
        "jobs": jobs,
        "applications": applications,
        "engagements": engagements,
        "workdays": [],
        "notifications": notifications,
        "listings": listings,
        "inquiries": inquiries,
        "advisories": advisories,
        "draft_listings": draft_listings,
        "blacklist": [
            {
                "id": "blacklist_badactor",
                "email": "badactor@kissan.in",
                "phone": "+91 99999 99999",
                "reason": "Previously reported for equipment misuse and defaulting on rental payment.",
                "created_at": current,
            }
        ],
        "voice_sessions": [
            {
                "id": "voice_demo",
                "user_id": farmer["id"],
                "session_id": "session_intern4_demo",
                "transcript": "Need two laborers for wheat harvesting and tractor tilling near Sinnar.",
                "language": "en-IN",
                "translated_text": "गेहूं की कटाई और ट्रैक्टर जुताई के लिए दो मजदूर चाहिए।",
                "source": "intern4-ai-transcriber",
                "metadata": {
                    "chunk_interval_seconds": 3,
                    "audio_codec": "opus/webm",
                    "primary_backend": "OpenAI Whisper",
                    "fallback_backend": "faster-whisper",
                },
                "created_at": current,
            }
        ],
    }


APP_STATE = seed_state()


def find_user(user_id: str) -> Dict[str, Any]:
    user = next((u for u in state()["users"] if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def enrich_equipment(item: Dict[str, Any]) -> Dict[str, Any]:
    owner = find_user(item["owner_id"])
    return {**item, "owner": public_user(owner)}


def enrich_job(item: Dict[str, Any]) -> Dict[str, Any]:
    farmer = find_user(item["farmer_id"])
    laborer = find_user(item["laborer_id"]) if item.get("laborer_id") else None
    application_count = len([a for a in state()["applications"] if a["job_id"] == item["id"]])
    return {
        **item,
        "farmer": public_user(farmer),
        "laborer": public_user(laborer) if laborer else None,
        "application_count": application_count,
    }


def enrich_application(item: Dict[str, Any]) -> Dict[str, Any]:
    job = next(j for j in state()["jobs"] if j["id"] == item["job_id"])
    laborer = find_user(item["laborer_id"])
    return {**item, "job": enrich_job(job), "laborer": public_user(laborer)}


def enrich_rental(item: Dict[str, Any]) -> Dict[str, Any]:
    equipment = next(e for e in state()["equipment"] if e["id"] == item["equipment_id"])
    renter = find_user(item["renter_id"])
    owner = find_user(item["owner_id"])
    return {
        **item,
        "equipment": enrich_equipment(equipment),
        "renter": public_user(renter),
        "owner": public_user(owner),
    }


def enrich_engagement(item: Dict[str, Any]) -> Dict[str, Any]:
    farmer = find_user(item["farmer_id"])
    worker = find_user(item["worker_id"])
    job = next((j for j in state()["jobs"] if j["id"] == item["job_id"]), None)
    return {
        **item,
        "farmer": public_user(farmer),
        "worker": public_user(worker),
        "job": enrich_job(job) if job else None,
    }


def find_listing(listing_id: str) -> Dict[str, Any]:
    listing = next((l for l in state()["listings"] if l["id"] == listing_id), None)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


def enrich_listing(item: Dict[str, Any]) -> Dict[str, Any]:
    farmer = find_user(item["farmer_id"])
    return {**item, "farmer": public_user(farmer)}


def enrich_inquiry(item: Dict[str, Any]) -> Dict[str, Any]:
    buyer = find_user(item["buyer_id"])
    farmer = find_user(item["farmer_id"])
    listing = find_listing(item["listing_id"])
    return {
        **item,
        "buyer": public_user(buyer),
        "farmer": public_user(farmer),
        "listing": enrich_listing(listing),
    }


def enrich_advisory(item: Dict[str, Any]) -> Dict[str, Any]:
    farmer = find_user(item["farmer_id"])
    return {**item, "farmer": public_user(farmer)}


def find_draft_listing(draft_id: str) -> Dict[str, Any]:
    draft = next((d for d in state()["draft_listings"] if d["id"] == draft_id), None)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft listing not found")
    return draft


def notify(user_id: str, type_: str, title: str, message: str, link: Optional[str] = None) -> Dict[str, Any]:
    item = {
        "id": make_id("note"),
        "user_id": user_id,
        "type": type_,
        "title": title,
        "message": message,
        "read": False,
        "link": link,
        "created_at": now_iso(),
    }
    state()["notifications"].insert(0, item)
    SupabaseStore.create("notifications", item, item)
    return item


def ensure_not_blacklisted(email: Optional[str], phone: Optional[str]):
    hit = next(
        (
            b for b in state()["blacklist"]
            if (email and b.get("email") == email) or (phone and b.get("phone") == phone)
        ),
        None,
    )
    if hit:
        raise HTTPException(status_code=403, detail=f"Blacklisted: {hit['reason']}")


@router.post("/seed")
def seed():
    global APP_STATE
    APP_STATE = seed_state()
    for table, rows in {
        "profiles": [public_user(u) for u in APP_STATE["users"]],
        "equipment": APP_STATE["equipment"],
        "rentals": APP_STATE["rentals"],
        "jobs": APP_STATE["jobs"],
        "applications": APP_STATE["applications"],
        "workdays": APP_STATE["workdays"],
        "notifications": APP_STATE["notifications"],
        "blacklist": APP_STATE["blacklist"],
        "engagements": APP_STATE["engagements"],
        "voice_sessions": APP_STATE["voice_sessions"],
    }.items():
        for row in rows:
            SupabaseStore.create(table, row, row)
    return {
        "seeded": True,
        "accounts": {
            "admin": {"email": "admin@kissan.in", "password": "admin123"},
            "farmer": {"email": "ramesh@kissan.in", "password": "farmer123"},
            "laborer": {"email": "suresh@kissan.in", "password": "labor123"},
        },
    }


@router.post("/auth/login")
def login(payload: LoginPayload):
    role = payload.role.upper()
    email = str(payload.email).lower() if payload.email else None
    phone = payload.phone
    user = next(
        (
            u for u in state()["users"]
            if u["role"] == role and ((email and u["email"] == email) or (phone and u["phone"] == phone))
        ),
        None,
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials for this portal")
    if payload.password and user["password_hash"] != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials for this portal")
    ensure_not_blacklisted(user["email"], user["phone"])
    if user["status"] == "BLACKLISTED":
        raise HTTPException(status_code=403, detail=f"Account blacklisted: {user.get('blacklist_reason')}")
    if user["status"] == "REJECTED":
        raise HTTPException(status_code=403, detail=f"Registration rejected: {user.get('admin_note')}")
    if user["status"] == "PENDING":
        raise HTTPException(status_code=403, detail="Registration is pending admin approval")
    return {"user": public_user(user)}


@router.post("/auth/register")
def register(payload: RegisterPayload):
    role = payload.role.upper()
    email = str(payload.email).lower()
    ensure_not_blacklisted(email, payload.phone)
    if any(u["email"] == email for u in state()["users"]):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = {
        "id": make_id("user"),
        "email": email,
        "password_hash": hash_password(payload.password),
        "full_name": payload.full_name,
        "phone": payload.phone,
        "role": role,
        "state": payload.state,
        "buyer_type": payload.buyer_type,
        "preferences": payload.preferences,
        "skills": payload.skills,
        "daily_rate": payload.daily_rate,
        "experience_yrs": payload.experience_yrs,
        "status": "PENDING",
        "blacklist_reason": None,
        "admin_note": "Awaiting admin verification.",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["users"].insert(0, user)
    SupabaseStore.create("profiles", public_user(user), public_user(user))
    notify("user_admin", "VERIFICATION", "New verification pending", f"{payload.full_name} registered as {role}.", "verifications")
    return {"user": public_user(user)}


@router.get("/me")
def me(user_id: str):
    return {"user": public_user(find_user(user_id))}


@router.get("/equipment")
def list_equipment(
    owner_id: Optional[str] = None,
    exclude_owner: Optional[str] = None,
    available_only: bool = False,
    q: str = "",
):
    items = state()["equipment"]
    if owner_id:
        items = [e for e in items if e["owner_id"] == owner_id]
    if exclude_owner:
        items = [e for e in items if e["owner_id"] != exclude_owner]
    if available_only:
        items = [e for e in items if e["available"]]
    if q:
        needle = q.lower()
        items = [e for e in items if needle in f"{e['name']} {e['category']} {e['description']} {e['location']}".lower()]
    return {"items": [enrich_equipment(e) for e in items]}


@router.post("/equipment")
def create_equipment(payload: EquipmentPayload):
    owner = find_user(payload.owner_id)
    if owner["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can list equipment")
    item = {
        "id": make_id("eq"),
        **payload.model_dump(),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["equipment"].insert(0, item)
    SupabaseStore.create("equipment", item, item)
    notify(payload.owner_id, "SYSTEM", "Equipment listed", f"{payload.name} is now listed for rent.", "my-equipment")
    return {"item": enrich_equipment(item)}


@router.patch("/equipment/{equipment_id}")
def update_equipment(equipment_id: str, payload: Dict[str, Any]):
    item = next((e for e in state()["equipment"] if e["id"] == equipment_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Equipment not found")
    allowed = {"name", "category", "description", "daily_rate", "location", "available"}
    item.update({k: v for k, v in payload.items() if k in allowed})
    item["updated_at"] = now_iso()
    SupabaseStore.update("equipment", equipment_id, item)
    return {"item": enrich_equipment(item)}


@router.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: str):
    before = len(state()["equipment"])
    state()["equipment"] = [e for e in state()["equipment"] if e["id"] != equipment_id]
    SupabaseStore.delete("equipment", equipment_id)
    return {"deleted": len(state()["equipment"]) != before}


@router.get("/rentals")
def list_rentals(user_id: Optional[str] = None):
    items = state()["rentals"]
    if user_id:
        items = [r for r in items if r["owner_id"] == user_id or r["renter_id"] == user_id]
    return {"items": [enrich_rental(r) for r in items]}


@router.post("/rentals")
def create_rental(payload: RentalPayload):
    equipment = next((e for e in state()["equipment"] if e["id"] == payload.equipment_id), None)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if not equipment["available"]:
        raise HTTPException(status_code=409, detail="Equipment is already rented out")
    renter = find_user(payload.renter_id)
    if renter["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can rent equipment")
    days = days_between(payload.start_date, payload.end_date)
    item = {
        "id": make_id("rent"),
        "equipment_id": equipment["id"],
        "renter_id": renter["id"],
        "owner_id": equipment["owner_id"],
        "status": "REQUESTED",
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "days": days,
        "total_cost": days * equipment["daily_rate"],
        "message": payload.message,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["rentals"].insert(0, item)
    SupabaseStore.create("rentals", item, item)
    notify(equipment["owner_id"], "RENTAL_REQUEST", "New rental request", f"{renter['full_name']} requested {equipment['name']}.", "my-rentals")
    notify(renter["id"], "RENTAL_REQUEST", "Rental request sent", f"Request sent for {equipment['name']}.", "my-rentals")
    return {"item": enrich_rental(item)}


@router.get("/engagements")
def list_engagements(farmer_id: Optional[str] = None, worker_id: Optional[str] = None, status: Optional[str] = None):
    items = state()["engagements"]
    if farmer_id:
        items = [e for e in items if e["farmer_id"] == farmer_id]
    if worker_id:
        items = [e for e in items if e["worker_id"] == worker_id]
    if status:
        items = [e for e in items if e["status"] == status.upper()]
    return {"items": [enrich_engagement(e) for e in items]}


@router.post("/engagements")
def create_engagement(payload: LaborEngagementPayload):
    farmer = find_user(payload.farmer_id)
    if farmer["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can create labor engagements")
    worker = find_user(payload.worker_id)
    if worker["role"] != "LABORER":
        raise HTTPException(status_code=403, detail="Only laborers can be engaged")
    if any(j.get("laborer_id") == worker["id"] and j["status"] in {"ASSIGNED", "ACTIVE"} for j in state()["jobs"]):
        raise HTTPException(status_code=409, detail="Laborer is already assigned to another farmer")
    job = next((j for j in state()["jobs"] if j["id"] == payload.job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["farmer_id"] != farmer["id"]:
        raise HTTPException(status_code=403, detail="Farmer can only engage labor for their own jobs")
    if job.get("laborer_id") and job["laborer_id"] != worker["id"]:
        raise HTTPException(status_code=409, detail="Job already assigned to another laborer")
    job["laborer_id"] = worker["id"]
    job["status"] = "ASSIGNED"
    job["updated_at"] = now_iso()
    item = {
        "id": make_id("eng"),
        "farmer_id": farmer["id"],
        "worker_id": worker["id"],
        "job_id": job["id"],
        "cost_per_laborer": payload.cost_per_laborer,
        "working_days": payload.working_days,
        "duration": payload.duration,
        "assigned_tasks": payload.assigned_tasks,
        "status": payload.status.upper(),
        "total_cost": payload.cost_per_laborer * payload.working_days,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["engagements"].insert(0, item)
    SupabaseStore.update("jobs", job["id"], job)
    SupabaseStore.create("engagements", item, item)
    notify(worker["id"], "LABOR_ENGAGED", "Labor assigned", f"{farmer['full_name']} engaged you for {job['title']}.", "my-job")
    notify(farmer["id"], "LABOR_ENGAGED", "Labor engagement created", f"{worker['full_name']} is working on {job['title']}.", "labor-hiring")
    return {"item": enrich_engagement(item)}


@router.patch("/rentals/{rental_id}")
def update_rental(rental_id: str, payload: RentalStatusPayload):
    rental = next((r for r in state()["rentals"] if r["id"] == rental_id), None)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    status = payload.status.upper()
    rental["status"] = status
    rental["updated_at"] = now_iso()
    equipment = next(e for e in state()["equipment"] if e["id"] == rental["equipment_id"])
    if status in {"ACCEPTED", "ACTIVE"}:
        equipment["available"] = False
    if status in {"COMPLETED", "REJECTED", "CANCELLED"}:
        equipment["available"] = True
    SupabaseStore.update("rentals", rental_id, rental)
    SupabaseStore.update("equipment", equipment["id"], equipment)
    notify(rental["owner_id"], f"RENTAL_{status}", "Rental updated", f"{equipment['name']} marked {status}.", "my-rentals")
    notify(rental["renter_id"], f"RENTAL_{status}", "Rental updated", f"{equipment['name']} marked {status}.", "my-rentals")
    return {"item": enrich_rental(rental)}


@router.get("/buyers")
def list_buyers(q: str = "", buyer_type: Optional[str] = None):
    items = [u for u in state()["users"] if u["role"] == "BUYER"]
    if buyer_type:
        items = [u for u in items if u.get("buyer_type", "").lower() == buyer_type.lower()]
    if q:
        needle = q.lower()
        items = [u for u in items if needle in f"{u['full_name']} {u.get('email','')} {u.get('phone','')} {u.get('preferences','') }".lower()]
    return {"items": [public_user(u) for u in items]}


@router.get("/listings")
def list_listings(
    farmer_id: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    q: str = "",
    buyer_id: Optional[str] = None,
    voice_query: Optional[str] = None,
):
    items = state()["listings"]
    if farmer_id:
        items = [l for l in items if l["farmer_id"] == farmer_id]
    if status:
        items = [l for l in items if l["status"] == status.lower()]
    if category:
        items = [l for l in items if category.lower() in l["category"].lower()]
    if location:
        items = [l for l in items if location.lower() in l["location"].lower()]
    if q:
        needle = q.lower()
        items = [l for l in items if needle in f"{l['name']} {l['category']} {l['description']} {l['location']}".lower()]
    if buyer_id or voice_query:
        buyer = find_user(buyer_id) if buyer_id else None
        for listing in items:
            score = 0
            if buyer and buyer.get("preferences"):
                for pref in buyer["preferences"] or []:
                    if pref and pref.lower() in f"{listing['name']} {listing['category']} {listing['description']}".lower():
                        score += 10
            if voice_query and voice_query.lower() in f"{listing['name']} {listing['category']} {listing['description']} {listing['location']}".lower():
                score += 5
            score += 1 if listing["status"] == "active" else 0
            listing["_match_score"] = score
        items = sorted(items, key=lambda x: x.get("_match_score", 0), reverse=True)
    return {"items": [enrich_listing(l) for l in items]}


@router.post("/listings")
def create_listing(payload: ListingPayload):
    farmer = find_user(payload.farmer_id)
    if farmer["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can create marketplace listings")
    item = {
        "id": make_id("list"),
        **payload.model_dump(),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["listings"].insert(0, item)
    SupabaseStore.create("listings", item, item)
    notify(payload.farmer_id, "LISTING_CREATED", "Listing published", f"{payload.name} is now live in the marketplace.", "marketplace")
    return {"item": enrich_listing(item)}


@router.patch("/listings/{listing_id}")
def update_listing(listing_id: str, payload: Dict[str, Any]):
    item = find_listing(listing_id)
    allowed = {"name", "category", "quantity_kg", "price_per_kg", "location", "description", "status"}
    item.update({k: v for k, v in payload.items() if k in allowed})
    item["updated_at"] = now_iso()
    SupabaseStore.update("listings", listing_id, item)
    return {"item": enrich_listing(item)}


@router.delete("/listings/{listing_id}")
def delete_listing(listing_id: str):
    item = find_listing(listing_id)
    state()["listings"] = [l for l in state()["listings"] if l["id"] != listing_id]
    SupabaseStore.delete("listings", listing_id)
    return {"deleted": True, "id": listing_id}


@router.post("/listings/ai-draft")
def create_ai_draft(payload: AIDraftPayload):
    title = payload.text or payload.voice_transcript or "Fresh produce listing"
    category = payload.category_hint or "General"
    description = payload.text or payload.voice_transcript or "AI draft listing created from user input."
    item = {
        "id": make_id("draft"),
        "farmer_id": "unknown",
        "name": title[:50],
        "category": category,
        "quantity_kg": payload.quantity_kg if hasattr(payload, 'quantity_kg') else 100.0,
        "price_per_kg": payload.price_per_kg if hasattr(payload, 'price_per_kg') else 0.0,
        "location": payload.location_hint or "Unknown",
        "description": description,
        "status": "draft",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["draft_listings"].insert(0, item)
    SupabaseStore.create("draft_listings", item, item)
    return {"draft": item}


@router.get("/draft-listings")
def list_draft_listings(farmer_id: Optional[str] = None):
    items = state()["draft_listings"]
    if farmer_id:
        items = [d for d in items if d["farmer_id"] == farmer_id]
    return {"items": items}


@router.post("/draft-listings")
def create_draft_listing(payload: DraftListingPayload):
    farmer = find_user(payload.farmer_id)
    if farmer["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can create draft listings")
    item = {
        "id": make_id("draft"),
        **payload.model_dump(),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["draft_listings"].insert(0, item)
    SupabaseStore.create("draft_listings", item, item)
    return {"item": item}


@router.patch("/draft-listings/{draft_id}")
def update_draft_listing(draft_id: str, payload: Dict[str, Any]):
    item = find_draft_listing(draft_id)
    allowed = {"name", "category", "quantity_kg", "price_per_kg", "location", "description", "status"}
    item.update({k: v for k, v in payload.items() if k in allowed})
    item["updated_at"] = now_iso()
    SupabaseStore.update("draft_listings", draft_id, item)
    return {"item": item}


@router.post("/draft-listings/{draft_id}/publish")
def publish_draft_listing(draft_id: str):
    draft = find_draft_listing(draft_id)
    if draft["status"] != "draft":
        raise HTTPException(status_code=409, detail="Only draft listings can be published")
    listing = {
        "id": make_id("list"),
        "farmer_id": draft["farmer_id"],
        "name": draft["name"],
        "category": draft["category"],
        "quantity_kg": draft["quantity_kg"],
        "price_per_kg": draft["price_per_kg"],
        "location": draft["location"],
        "description": draft.get("description"),
        "status": "active",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["listings"].insert(0, listing)
    state()["draft_listings"] = [d for d in state()["draft_listings"] if d["id"] != draft_id]
    SupabaseStore.create("listings", listing, listing)
    SupabaseStore.delete("draft_listings", draft_id)
    notify(draft["farmer_id"], "LISTING_PUBLISHED", "Draft published", f"{draft['name']} has been published.", "marketplace")
    return {"item": enrich_listing(listing)}


@router.get("/inquiries")
def list_inquiries(
    buyer_id: Optional[str] = None,
    farmer_id: Optional[str] = None,
    listing_id: Optional[str] = None,
    status: Optional[str] = None,
):
    items = state()["inquiries"]
    if buyer_id:
        items = [i for i in items if i["buyer_id"] == buyer_id]
    if farmer_id:
        items = [i for i in items if i["farmer_id"] == farmer_id]
    if listing_id:
        items = [i for i in items if i["listing_id"] == listing_id]
    if status:
        items = [i for i in items if i["status"] == status.lower()]
    return {"items": [enrich_inquiry(i) for i in items]}


@router.post("/inquiries")
def create_inquiry(payload: InquiryPayload):
    buyer = find_user(payload.buyer_id)
    if buyer["role"] != "BUYER":
        raise HTTPException(status_code=403, detail="Only buyers can send inquiries")
    farmer = find_user(payload.farmer_id)
    if farmer["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Inquiries must target a farmer")
    listing = find_listing(payload.listing_id)
    if listing["status"] != "active":
        raise HTTPException(status_code=409, detail="Listing is not available")
    if any(i["buyer_id"] == buyer["id"] and i["listing_id"] == listing["id"] for i in state()["inquiries"]):
        raise HTTPException(status_code=409, detail="Inquiry already submitted")
    quantity = payload.quantity_kg if hasattr(payload, "quantity_kg") else None
    expected_commission = 0.0
    if quantity:
        expected_commission = round(quantity * listing["price_per_kg"] * 0.03, 2)
    item = {
        "id": make_id("inq"),
        "buyer_id": buyer["id"],
        "farmer_id": farmer["id"],
        "listing_id": listing["id"],
        "message": payload.message,
        "quantity_kg": quantity,
        "status": "pending",
        "commission_rate": 0.03,
        "expected_commission": expected_commission,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["inquiries"].insert(0, item)
    SupabaseStore.create("inquiries", item, item)
    notify(farmer["id"], "INQUIRY_RECEIVED", "New buyer inquiry", f"{buyer['full_name']} inquired about {listing['name']}", "marketplace-inquiries")
    notify(buyer["id"], "INQUIRY_SUBMITTED", "Inquiry sent", f"Inquiry sent for {listing['name']}", "my-inquiries")
    return {"item": enrich_inquiry(item)}


@router.patch("/inquiries/{inquiry_id}")
def update_inquiry(inquiry_id: str, payload: InquiryStatusPayload):
    inquiry = next((i for i in state()["inquiries"] if i["id"] == inquiry_id), None)
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    status = payload.status.lower()
    if status not in {"pending", "accepted", "declined"}:
        raise HTTPException(status_code=400, detail="Invalid inquiry status")
    inquiry["status"] = status
    inquiry["updated_at"] = now_iso()
    buyer_id = inquiry["buyer_id"]
    notify(buyer_id, "INQUIRY_UPDATED", "Inquiry status updated", f"Your inquiry is {status}.", "my-inquiries")
    return {"item": enrich_inquiry(inquiry)}


def generate_advisory(payload: AdvisoryPayload) -> tuple[str, float, str]:
    text = (payload.description or payload.input_reference or "").lower()
    if any(token in text for token in ["spot", "yellow", "mold", "blight", "rust", "fungal"]):
        return (
            "Fungal infection",
            0.75,
            "Apply a copper-based fungicide, improve air circulation, and avoid overwatering.",
        )
    if any(token in text for token in ["worm", "pest", "aphid", "moth", "bollworm"]):
        return (
            "Pest infestation",
            0.72,
            "Use neem oil or biopesticide and remove affected leaves.",
        )
    return (
        "Nutrient deficiency or general stress",
        0.65,
        "Use a balanced NPK fertilizer and test soil moisture.",
    )


@router.get("/advisories")
def list_advisories(farmer_id: Optional[str] = None):
    items = state()["advisories"]
    if farmer_id:
        items = [a for a in items if a["farmer_id"] == farmer_id]
    return {"items": [enrich_advisory(a) for a in items]}


@router.post("/advisories")
def create_advisory(payload: AdvisoryPayload):
    farmer = find_user(payload.farmer_id)
    if farmer["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can request crop advisory")
    diagnosis, probability, recommendation = generate_advisory(payload)
    item = {
        "id": make_id("adv"),
        **payload.model_dump(),
        "diagnosis": diagnosis,
        "probability": probability,
        "recommendation": recommendation,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["advisories"].insert(0, item)
    SupabaseStore.create("advisories", item, item)
    notify(payload.farmer_id, "ADVISORY_READY", "Crop advisory available", "Your crop advisory report is ready.", "advisory-history")
    return {"item": enrich_advisory(item)}


@router.get("/admin/listings")
def admin_listings(status: Optional[str] = None, q: str = ""):
    items = state()["listings"]
    if status:
        items = [l for l in items if l["status"] == status.lower()]
    if q:
        needle = q.lower()
        items = [l for l in items if needle in f"{l['name']} {l['category']} {l['description']} {l['location']}".lower()]
    return {"items": [enrich_listing(l) for l in items]}


@router.post("/admin/listings/{listing_id}/flag")
def flag_listing(listing_id: str, reason: Dict[str, str]):
    listing = find_listing(listing_id)
    listing["status"] = "flagged"
    listing["updated_at"] = now_iso()
    listing["flag_reason"] = reason.get("reason")
    SupabaseStore.update("listings", listing_id, listing)
    return {"item": enrich_listing(listing)}


@router.get("/admin/inquiries")
def admin_inquiries(status: Optional[str] = None):
    items = state()["inquiries"]
    if status:
        items = [i for i in items if i["status"] == status.lower()]
    return {"items": [enrich_inquiry(i) for i in items]}


@router.get("/admin/advisories")
def admin_advisories():
    return {"items": [enrich_advisory(a) for a in state()["advisories"]]}


@router.get("/admin/market-stats")
def admin_market_stats():
    listings = state()["listings"]
    inquiries = state()["inquiries"]
    advisories = state()["advisories"]
    return {
        "total_listings": len(listings),
        "active_listings": len([l for l in listings if l["status"] == "active"]),
        "flagged_listings": len([l for l in listings if l["status"] == "flagged"]),
        "open_inquiries": len([i for i in inquiries if i["status"] == "pending"]),
        "accepted_inquiries": len([i for i in inquiries if i["status"] == "accepted"]),
        "declined_inquiries": len([i for i in inquiries if i["status"] == "declined"]),
        "advisory_requests": len(advisories),
        "top_categories": sorted(
            {cat: sum(1 for l in listings if l["category"] == cat) for cat in {l["category"] for l in listings}}.items(),
            key=lambda x: x[1],
            reverse=True,
        ),
    }


@router.get("/admin/stats")
def admin_stats():
    users = state()["users"]
    non_admin = [u for u in users if u["role"] != "ADMIN"]
    approved = len([u for u in non_admin if u["status"] == "APPROVED"])
    return {
        "pending_verifications": len([u for u in non_admin if u["status"] == "PENDING"]),
        "approved_users": approved,
        "blacklisted": len([u for u in non_admin if u["status"] == "BLACKLISTED"]),
        "total_users": len(users),
        "farmers": len([u for u in users if u["role"] == "FARMER"]),
        "laborers": len([u for u in users if u["role"] == "LABORER"]),
        "buyers": len([u for u in users if u["role"] == "BUYER"]),
        "equipment_listed": len(state()["equipment"]),
        "open_jobs": len([j for j in state()["jobs"] if j["status"] == "OPEN"]),
        "total_jobs": len(state()["jobs"]),
        "total_rentals": len(state()["rentals"]),
        "active_rentals": len([r for r in state()["rentals"] if r["status"] in {"ACCEPTED", "ACTIVE"}]),
        "total_listings": len(state()["listings"]),
        "active_listings": len([l for l in state()["listings"] if l["status"] == "active"]),
        "open_inquiries": len([i for i in state()["inquiries"] if i["status"] == "pending"]),
        "advisory_requests": len(state()["advisories"]),
        "compliance_percent": round((approved / max(1, len(non_admin))) * 100),
    }


@router.get("/jobs")
def list_jobs(
    farmer_id: Optional[str] = None,
    laborer_id: Optional[str] = None,
    open_only: bool = False,
    exclude_applied_by: Optional[str] = None,
    q: str = "",
):
    items = state()["jobs"]
    if farmer_id:
        items = [j for j in items if j["farmer_id"] == farmer_id]
    if laborer_id:
        items = [j for j in items if j.get("laborer_id") == laborer_id]
    if open_only:
        items = [j for j in items if j["status"] == "OPEN"]
    if exclude_applied_by:
        applied_ids = {a["job_id"] for a in state()["applications"] if a["laborer_id"] == exclude_applied_by}
        items = [j for j in items if j["id"] not in applied_ids]
    if q:
        needle = q.lower()
        items = [j for j in items if needle in f"{j['title']} {j['description']} {j['location']} {j['required_skill']}".lower()]
    return {"items": [enrich_job(j) for j in items]}


@router.post("/jobs")
def create_job(payload: JobPayload):
    farmer = find_user(payload.farmer_id)
    if farmer["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can post jobs")
    item = {
        "id": make_id("job"),
        **payload.model_dump(),
        "laborer_id": None,
        "status": "OPEN",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    state()["jobs"].insert(0, item)
    SupabaseStore.create("jobs", item, item)
    notify(payload.farmer_id, "SYSTEM", "Job posted", f"{payload.title} is open for applications.", "labor-hiring")
    return {"item": enrich_job(item)}


@router.patch("/jobs/{job_id}/complete")
def complete_job(job_id: str):
    job = next((j for j in state()["jobs"] if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job["status"] = "COMPLETED"
    job["updated_at"] = now_iso()
    SupabaseStore.update("jobs", job_id, job)
    if job.get("laborer_id"):
        notify(job["laborer_id"], "JOB_COMPLETED", "Job completed", f"{job['title']} has been completed.", "my-job")
    return {"item": enrich_job(job)}


@router.get("/applications")
def list_applications(job_id: Optional[str] = None, laborer_id: Optional[str] = None, farmer_id: Optional[str] = None):
    items = state()["applications"]
    if job_id:
        items = [a for a in items if a["job_id"] == job_id]
    if laborer_id:
        items = [a for a in items if a["laborer_id"] == laborer_id]
    if farmer_id:
        farmer_jobs = {j["id"] for j in state()["jobs"] if j["farmer_id"] == farmer_id}
        items = [a for a in items if a["job_id"] in farmer_jobs]
    return {"items": [enrich_application(a) for a in items]}


@router.post("/applications")
def create_application(payload: ApplicationPayload):
    job = next((j for j in state()["jobs"] if j["id"] == payload.job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "OPEN":
        raise HTTPException(status_code=409, detail="Job is not open")
    laborer = find_user(payload.laborer_id)
    if laborer["role"] != "LABORER":
        raise HTTPException(status_code=403, detail="Only laborers can apply")
    active_job = next((j for j in state()["jobs"] if j.get("laborer_id") == laborer["id"] and j["status"] in {"ASSIGNED", "ACTIVE"}), None)
    if active_job:
        raise HTTPException(status_code=409, detail="Laborer is already assigned to another farmer")
    if any(a["job_id"] == payload.job_id and a["laborer_id"] == payload.laborer_id for a in state()["applications"]):
        raise HTTPException(status_code=409, detail="Already applied")
    item = {
        "id": make_id("app"),
        "job_id": payload.job_id,
        "laborer_id": payload.laborer_id,
        "status": "PENDING",
        "message": payload.message,
        "created_at": now_iso(),
    }
    state()["applications"].insert(0, item)
    SupabaseStore.create("applications", item, item)
    notify(job["farmer_id"], "JOB_APPLICATION", "New job application", f"{laborer['full_name']} applied for {job['title']}.", "labor-hiring")
    return {"item": enrich_application(item)}


@router.patch("/applications/{application_id}")
def update_application(application_id: str, payload: ApplicationStatusPayload):
    app = next((a for a in state()["applications"] if a["id"] == application_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    status = payload.status.upper()
    job = next(j for j in state()["jobs"] if j["id"] == app["job_id"])
    if status == "ACCEPTED":
        active_job = next((j for j in state()["jobs"] if j.get("laborer_id") == app["laborer_id"] and j["status"] in {"ASSIGNED", "ACTIVE"}), None)
        if active_job and active_job["id"] != job["id"]:
            raise HTTPException(status_code=409, detail="Laborer is already assigned to another farmer")
        job["laborer_id"] = app["laborer_id"]
        job["status"] = "ASSIGNED"
        for other in state()["applications"]:
            if other["job_id"] == job["id"] and other["id"] != app["id"]:
                other["status"] = "REJECTED"
        notify(app["laborer_id"], "JOB_ASSIGNED", "Application accepted", f"You are assigned to {job['title']}.", "my-job")
    app["status"] = status
    job["updated_at"] = now_iso()
    SupabaseStore.update("applications", application_id, app)
    SupabaseStore.update("jobs", job["id"], job)
    return {"item": enrich_application(app)}


@router.get("/workdays")
def list_workdays(job_id: Optional[str] = None, laborer_id: Optional[str] = None):
    items = state()["workdays"]
    if job_id:
        items = [w for w in items if w["job_id"] == job_id]
    if laborer_id:
        items = [w for w in items if w["laborer_id"] == laborer_id]
    return {"items": items}


@router.post("/workdays")
def create_workday(payload: WorkdayPayload):
    if any(w["job_id"] == payload.job_id and w["date"] == payload.date for w in state()["workdays"]):
        raise HTTPException(status_code=409, detail="Attendance already marked for this date")
    item = {"id": make_id("workday"), **payload.model_dump(), "created_at": now_iso()}
    state()["workdays"].insert(0, item)
    SupabaseStore.create("workdays", item, item)
    return {"item": item}


@router.get("/dashboard/farmer")
def farmer_dashboard(farmer_id: str):
    farmer = find_user(farmer_id)
    if farmer["role"] != "FARMER":
        raise HTTPException(status_code=403, detail="Only farmers can access this dashboard")
    equipment = [enrich_equipment(e) for e in state()["equipment"] if e["owner_id"] == farmer_id]
    rentals = [enrich_rental(r) for r in state()["rentals"] if r["owner_id"] == farmer_id or r["renter_id"] == farmer_id]
    jobs = [enrich_job(j) for j in state()["jobs"] if j["farmer_id"] == farmer_id]
    engagements = [enrich_engagement(e) for e in state()["engagements"] if e["farmer_id"] == farmer_id]
    hired_workers = {e["worker_id"] for e in state()["engagements"] if e["farmer_id"] == farmer_id}
    total_cost = sum(e["total_cost"] for e in state()["engagements"] if e["farmer_id"] == farmer_id)
    return {
        "farmer": public_user(farmer),
        "equipment": equipment,
        "rentals": rentals,
        "jobs": jobs,
        "engagements": engagements,
        "labor_hiring": {
            "laborers_hired": len(hired_workers),
            "total_cost": total_cost,
            "working_engagements": len(engagements),
            "active_engagements": len([e for e in engagements if e["status"] in {"ACTIVE", "ASSIGNED"}]),
        },
    }


@router.get("/dashboard/labor")
def labor_dashboard(laborer_id: str):
    laborer = find_user(laborer_id)
    if laborer["role"] != "LABORER":
        raise HTTPException(status_code=403, detail="Only laborers can access this dashboard")
    current_engagement = next((e for e in state()["engagements"] if e["worker_id"] == laborer_id and e["status"] in {"ACTIVE", "ASSIGNED"}), None)
    current_job = enrich_job(next((j for j in state()["jobs"] if j["id"] == current_engagement["job_id"]), None)) if current_engagement else None
    workdays = [w for w in state()["workdays"] if w["laborer_id"] == laborer_id]
    available_jobs = [enrich_job(j) for j in state()["jobs"] if j["status"] == "OPEN" and j["id"] not in {a["job_id"] for a in state()["applications"] if a["laborer_id"] == laborer_id}]
    return {
        "laborer": public_user(laborer),
        "current_engagement": enrich_engagement(current_engagement) if current_engagement else None,
        "current_job": current_job,
        "workdays": workdays,
        "available_jobs": available_jobs,
    }


@router.get("/notifications")
def list_notifications(user_id: Optional[str] = None):
    items = state()["notifications"]
    if user_id:
        items = [n for n in items if n["user_id"] == user_id]
    return {"items": items, "unread_count": len([n for n in items if not n["read"]])}


@router.post("/notifications/read-all")
def read_all_notifications(user_id: str):
    for item in state()["notifications"]:
        if item["user_id"] == user_id:
            item["read"] = True
    return {"ok": True}


@router.get("/admin/stats")
def admin_stats():
    users = state()["users"]
    non_admin = [u for u in users if u["role"] != "ADMIN"]
    approved = len([u for u in non_admin if u["status"] == "APPROVED"])
    return {
        "pending_verifications": len([u for u in non_admin if u["status"] == "PENDING"]),
        "approved_users": approved,
        "blacklisted": len([u for u in non_admin if u["status"] == "BLACKLISTED"]),
        "total_users": len(users),
        "farmers": len([u for u in users if u["role"] == "FARMER"]),
        "laborers": len([u for u in users if u["role"] == "LABORER"]),
        "equipment_listed": len(state()["equipment"]),
        "open_jobs": len([j for j in state()["jobs"] if j["status"] == "OPEN"]),
        "total_jobs": len(state()["jobs"]),
        "total_rentals": len(state()["rentals"]),
        "active_rentals": len([r for r in state()["rentals"] if r["status"] in {"ACCEPTED", "ACTIVE"}]),
        "compliance_percent": round((approved / max(1, len(non_admin))) * 100),
    }


@router.get("/admin/users")
def admin_users(role: Optional[str] = None, status: Optional[str] = None, q: str = ""):
    users = [public_user(u) for u in state()["users"]]
    if role:
        users = [u for u in users if u["role"] == role.upper()]
    if status:
        users = [u for u in users if u["status"] == status.upper()]
    if q:
        needle = q.lower()
        users = [u for u in users if needle in f"{u['full_name']} {u['email']} {u['phone']}".lower()]
    return {"items": users}


@router.patch("/admin/users/{user_id}")
def verify_user(user_id: str, payload: VerificationPayload):
    user = find_user(user_id)
    user["status"] = payload.status.upper()
    user["admin_note"] = payload.admin_note
    user["updated_at"] = now_iso()
    if user["status"] == "BLACKLISTED":
        user["blacklist_reason"] = payload.admin_note or "Blacklisted by admin"
    SupabaseStore.update("profiles", user_id, public_user(user))
    notify(user_id, "VERIFICATION", "Verification updated", f"Your account status is now {user['status']}.", None)
    return {"user": public_user(user)}


@router.get("/admin/blacklist")
def list_blacklist():
    return {"items": state()["blacklist"]}


@router.post("/admin/blacklist")
def add_blacklist(payload: BlacklistPayload):
    item = {
        "id": make_id("blacklist"),
        "email": str(payload.email).lower() if payload.email else None,
        "phone": payload.phone,
        "reason": payload.reason,
        "created_at": now_iso(),
    }
    state()["blacklist"].insert(0, item)
    for user in state()["users"]:
        if (item["email"] and user["email"] == item["email"]) or (item["phone"] and user["phone"] == item["phone"]):
            user["status"] = "BLACKLISTED"
            user["blacklist_reason"] = item["reason"]
            notify(user["id"], "BLACKLIST", "Account blacklisted", item["reason"], None)
    SupabaseStore.create("blacklist", item, item)
    return {"item": item}


@router.delete("/admin/blacklist/{entry_id}")
def delete_blacklist(entry_id: str):
    before = len(state()["blacklist"])
    state()["blacklist"] = [b for b in state()["blacklist"] if b["id"] != entry_id]
    SupabaseStore.delete("blacklist", entry_id)
    return {"deleted": len(state()["blacklist"]) != before}


@router.get("/voice-sessions")
def list_voice_sessions(user_id: Optional[str] = None):
    items = state()["voice_sessions"]
    if user_id:
        items = [v for v in items if v.get("user_id") == user_id]
    return {"items": items}


@router.post("/voice-sessions")
def create_voice_session(payload: VoiceSessionPayload):
    item = {"id": make_id("voice"), **payload.model_dump(), "created_at": now_iso()}
    state()["voice_sessions"].insert(0, item)
    SupabaseStore.create("voice_sessions", item, item)
    if payload.user_id:
        notify(payload.user_id, "VOICE_TRANSCRIPT", "Voice transcript saved", "Intern4 AI transcriber saved a new transcript.", "voice")
    return {"item": item}
