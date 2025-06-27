from fastapi import APIRouter
from .news import router as _news_router
from .report import router as _ai_router
from .support import router as _support_router
from .user import router as _user_router
from .subscription import router as _subscription_router
from .referral import router as _referral_router
from .filter import router as _filter_router
from .yookassa import router as _yookassa_router
from .payment import router as _payment_router

router = APIRouter()

router.include_router(router=_news_router, prefix="/news", tags=["News"])
router.include_router(router=_user_router, prefix="/user", tags=["User"])
router.include_router(router=_ai_router, prefix="/report", tags=["Report"])
router.include_router(router=_filter_router, prefix="/filter", tags=["Filter"])
router.include_router(router=_support_router, prefix="/support", tags=["Support"])
router.include_router(router=_referral_router, prefix="/referral", tags=["Referral"])
router.include_router(router=_yookassa_router, prefix="/callback", tags=["Callback"])
router.include_router(router=_payment_router, prefix="/payment", tags=["Payment"])
router.include_router(
    router=_subscription_router, prefix="/subscription", tags=["Subscription"]
)

__all__ = ["router"]
