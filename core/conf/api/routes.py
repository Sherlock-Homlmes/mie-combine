# libraries
from fastapi import APIRouter

# local
from api import stats

# create all api routers
api_router = APIRouter()
all_routers = (stats,)

for router in all_routers:
    api_router.include_router(
        router.router,
        prefix="/api",
        responses={404: {"description": "Not found"}},
    )
