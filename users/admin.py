from django.contrib import admin
from fitness_django.settings import AUTH_USER_MODEL
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "user_id")
    list_filter = ("updated_at",)

    class Meta:
        model = User


admin.site.register(User, UserAdmin)
