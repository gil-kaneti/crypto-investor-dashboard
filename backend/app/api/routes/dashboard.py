from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import CoinPricesSection, DashboardResponse
from app.services.dashboard_service import build_coin_prices_section, build_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def read_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return build_dashboard(db, current_user)


@router.get("/coin-prices", response_model=CoinPricesSection)
def read_coin_prices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CoinPricesSection:
    return build_coin_prices_section(db, current_user)
