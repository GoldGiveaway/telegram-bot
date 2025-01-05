from handlers.main import router as main_router
from handlers.giveaway import router as giveaway_router
from handlers.admin import router as admin_router

routers = (
    main_router,
    giveaway_router,
    admin_router
)
