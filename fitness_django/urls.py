from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from users.views import (
    CreateUpdateUserView,
    LoginUserView,
    ProfileInfoView,
    WeightHistoryView,
    LogoutUserView,
    UpdateUserView,
    PredictCyclePhaseView
)

# Create a router for ViewSets
router = DefaultRouter()


urlpatterns = [
    path("admin/", admin.site.urls),

    # User create API endpoint
    path("api/users/create/", CreateUpdateUserView.as_view(), name="users-create"),
    path("api/users/profile/", ProfileInfoView.as_view(), name="profile_info_view"),
    path("api/users/weights/", WeightHistoryView.as_view(), name="weight_history_view"),
    path("api/users/login/", LoginUserView.as_view(), name="users-login"),
    path("api/users/logout/", LogoutUserView.as_view(), name="users-logout"),
    path("api/users/update/", UpdateUserView.as_view(), name="users-update"),
    path("api/users/predict_cycle_phase/", PredictCyclePhaseView.as_view(), name="predict-cycle-phase")
]
