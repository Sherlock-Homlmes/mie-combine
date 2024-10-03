# libraries
from fastapi import APIRouter

# local
from api import server_stats, user_stats

# create all api routers
app_router = APIRouter()
api_routers = (server_stats,)
template_routers = (user_stats,)

for router in api_routers:
    app_router.include_router(
        router.router,
        prefix="/api",
        responses={404: {"description": "Not found"}},
    )

for router in template_routers:
    app_router.include_router(
        router.router,
        responses={404: {"description": "Not found"}},
    )
