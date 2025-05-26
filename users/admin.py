from django.contrib import admin
from fitness_django.settings import AUTH_USER_MODEL


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user_id",
        "app_first_name",
        "sap_user",
        "phone_number",
        "is_active",
        "banned",
        "created_at",
    )
    list_filter = ["is_active", "is_staff"]
    search_fields = ["user_id", "app_first_name", "phone_number", "sap_user__iin"]
    raw_id_fields = [
        "sap_user",
    ]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("user_id", "staff_email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "full_name",
                    "app_first_name",
                    "app_username",
                    "phone_number",
                    "sap_user",
                    "authentication_email",
                    "app_password",
                    "sub",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "esed_work_status",
                    "banned",
                    "groups",
                )
            },
        ),
        ("Important dates", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("staff_email", "password1", "password2")},
        ),
    )

    class Meta:
        model = AUTH_USER_MODEL
