"""
API routes package.
"""

from api.routes.health import router as health_router
from api.routes.rainfall import router as rainfall_router
from api.routes.overflow import router as overflow_router
from api.routes.alerts import router as alerts_router
from api.routes.demo import router as demo_router

__all__ = [
    "health_router",
    "rainfall_router",
    "overflow_router",
    "alerts_router",
    "demo_router",
]
