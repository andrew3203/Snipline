from fastapi import APIRouter
from .news import router as _news_router
from .healthcheck import router as _healthcheck_router


router = APIRouter()

router.include_router(_healthcheck_router)
router.include_router(_news_router, prefix="/news", tags=["News"])