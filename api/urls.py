from django.urls import path
from api import views as ApiViews

app_name = "api"

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("register/", TokenObtainPairView.as_view(), name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("movies/", ApiViews.MoviesListViews.as_view(), name="movies-list"),
    path(
        "collection/", ApiViews.CollectListCreateViews.as_view(), name="collection-list"
    ),
    path(
        "collection/<str:collection_uuid>/",
        ApiViews.CollectUpdateViews.as_view(),
        name="collection",
    ),
    path("request-count/", ApiViews.RequestView, name="request_count"),
    path("request-count/reset/", ApiViews.RequestResetView, name="request_count_reset"),
]
