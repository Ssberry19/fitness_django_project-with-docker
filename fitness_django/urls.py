from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from recommendation.views import RecommendationAPIView
from nutrition.views import NutritionAPIView
from tracking.views import WeightEntryViewSet, WeightHistoryAPIView
from modelinfo.views import ModelFeaturesAPIView
from users.views import (
    CreateUpdateUserView,
    LoginUserView,
    ProfileInfoView,
    WeightHistoryView,
    LogoutUserView,
    UpdateUserView
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r"weight-entries", WeightEntryViewSet, basename="weight-entry")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Recommendation API endpoint
    path("api/recommendation/", RecommendationAPIView.as_view(), name="recommendation"),
    # Nutrition API endpoint
    path("api/nutrition/", NutritionAPIView.as_view(), name="nutrition"),
    # Weight tracking API endpoints
    path("api/", include(router.urls)),
    path("api/weight-history/", WeightHistoryAPIView.as_view(), name="weight-history"),
    # Model features API endpoint
    path("api/model-features/", ModelFeaturesAPIView.as_view(), name="model-features"),
    # User create API endpoint
    path("api/users/create/", CreateUpdateUserView.as_view(), name="users-create"),
    path("api/users/profile/", ProfileInfoView.as_view(), name="profile_info_view"),
    path("api/users/weights/", WeightHistoryView.as_view(), name="weight_history_view"),
    path("api/users/login/", LoginUserView.as_view(), name="users-login"),
    path("api/users/logout/", LogoutUserView.as_view(), name="users-logout"),
    path("api/users/update/", UpdateUserView.as_view(), name="users-update")
]
