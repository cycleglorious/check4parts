from fastapi import APIRouter, Depends
from app.adapters.bm_parts_adapter import BMPartsAdapter
from app.api.auth import get_current_user
