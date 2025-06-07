from django.contrib import admin
from fitness_django.settings import AUTH_USER_MODEL
from users.models import User, WeightModel, Allergen
from rest_framework.authtoken.models import Token


class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "email", "username")
    list_filter = ("updated_at",)

    class Meta:
        model = User


class WeightAdmin(admin.ModelAdmin):
    list_display = ("pk", "weight")
    list_filter = ("updated_at",)

    class Meta:
        model = WeightModel

class AllergenAdmin(admin.ModelAdmin):
    list_display = ("name", )

    class Meta:
        model = Allergen

class FilterTokenAdmin(admin.ModelAdmin):
    search_fields = ["user__email", "user__full_name"]


admin.site.register(User, UserAdmin)
admin.site.register(WeightModel, WeightAdmin)
admin.site.register(Token, FilterTokenAdmin)
admin.site.register(Allergen, AllergenAdmin)
