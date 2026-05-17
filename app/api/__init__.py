from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.habits import router as habits_router
from app.api.groups import router as groups_router
from app.api.messages import router as messages_router
from app.api.wellness import router as wellness_router
from app.api.analytics import router as analytics_router

api_router = {
    "auth": auth_router,
    "posts": posts_router,
    "habits": habits_router,
    "groups": groups_router,
    "messages": messages_router,
    "wellness": wellness_router,
    "analytics": analytics_router,
}
