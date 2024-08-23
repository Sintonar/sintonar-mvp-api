from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sintonar.apps.match.views.match import MatchViewSet, UserMatchViewSet

router = DefaultRouter()
router.register("users", UserMatchViewSet, basename="user_match")
router.register("", MatchViewSet, basename="match")


urlpatterns = [
    path("", include(router.urls)),
]
