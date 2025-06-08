import datetime
import requests

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin, User
from django.conf import settings


class HeightModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Height", null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Changed")

    def __str__(self):
        return str(self.height)


class WeightModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Weight", null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Changed")

    def __str__(self):
        return str(self.weight)


class CycleModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Added")


class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, **extra_fields: dict) -> User:
        user = self.model(is_superuser=False, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields: tuple) -> User:
        if not email:
            raise ValueError("Please provide an email")
        user = self.model(
            email=email,
            username=email,
            is_staff=True,
            is_superuser=True,
            age=10,
            gender=1,
            target_weight=10,
            goal=1,
            activity_level=1,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email: str) -> User:
        return self.get(**{self.model.USERNAME_FIELD + "__iexact": email})

    def get(self, **kwargs: dict) -> User:
        if "email" in kwargs:
            kwargs["email__iexact"] = kwargs["email"]
            del kwargs["email"]
        return super().get(**kwargs)

    def update_or_create(self, defaults, **kwargs: dict) -> tuple[User, bool]:
        new_info = kwargs.copy()
        new_info.update(defaults) if defaults else {}
        created = True
        try:
            obj = self.get(email=kwargs["email"])
            for key, value in new_info.items():
                setattr(obj, key, value)
            obj.save()
            created = False
        except User.DoesNotExist:
            obj = User(**new_info)
            obj.save()
        return obj, created


class User(AbstractUser, PermissionsMixin):
    # Constants

    MAN = 1
    WOMAN = 2
    GENDERS = [
        (MAN, "Male"),
        (WOMAN, "Female"),
    ]

    WEIGHT_LOSS = 1
    WEIGHT_GAIN = 2
    MAINTENANCE = 3
    GOALS = [
        (WEIGHT_LOSS, "Weight loss"),
        (WEIGHT_GAIN, "Weight gain"),
        (MAINTENANCE, "Maintenance"),
    ]

    SEDENTARY = 1
    LIGHT = 2
    MODERATE = 3
    HIGH = 4
    EXTREME = 5
    ACTIVITY_LEVELS = [
        (SEDENTARY, "Sedentary"),
        (LIGHT, "Light"),
        (MODERATE, "Moderate"),
        (HIGH, "Hight"),
        (EXTREME, "Extreme"),
    ]

    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_staff = models.BooleanField(default=False, verbose_name="Admin")

    # Main info
    birth_date = models.DateTimeField(null=True, blank=True, verbose_name="Birth Date")
    age = models.IntegerField(verbose_name="Age", null=True, blank=True)
    gender = models.IntegerField(choices=GENDERS, verbose_name="Gender")
    email = models.CharField(max_length=255, null=True, unique=True)

    # Parameters
    height = models.ForeignKey(
        HeightModel,
        on_delete=models.CASCADE,
        related_name="Height",
        verbose_name="Height",
        null=True,
        blank=True,
    )
    weight = models.ForeignKey(
        WeightModel,
        on_delete=models.CASCADE,
        related_name="Weight",
        verbose_name="Weight",
        null=True,
        blank=True,
    )
    target_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Target weight"
    )

    # Goal, Activity level
    goal = models.IntegerField(choices=GOALS, verbose_name="Goal")
    activity_level = models.IntegerField(
        choices=ACTIVITY_LEVELS, verbose_name="Activity level"
    )

    # Cycles
    menstrual_phase = models.CharField(max_length=255, null=True, unique=True)
    cycle_record_json = models.JSONField(default=dict, blank=True, null=True)
    cycle_length = models.IntegerField(
        null=True, blank=True, verbose_name="Cycle length in days"
    )
    last_period_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Last period date"
    )
    cycle_day = models.IntegerField(
        null=True, blank=True, verbose_name="Current cycle day"
    )

    # Allergens
    allergens = models.ManyToManyField(Allergen, blank=True)

    # Stored metrics
    bmi = models.FloatField(null=True, blank=True, verbose_name="Body mass index")
    bfp = models.FloatField(null=True, blank=True, verbose_name="Body Fat Percentage")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Added")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Changed")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Initialize BMI and BFP as None by default
        self.bmi = None
        self.bfp = None

        # Ensure weight and height exist before calculating BMI
        if self.weight and self.height and float(self.height.height) > 0:
            try:
                weight_value = float(self.weight.weight)
                height_value = float(self.height.height)
                # Convert height to meters by dividing by 100
                height_m = float(height_value) / 100
                self.bmi = round(weight_value / (height_m**2), 2)
            except (ValueError, TypeError):
                print("TRACEBACK!!!")
                import traceback

                print(traceback.print_exc)
                pass  # If weight or height can't be converted to float

        # Calculate age from birth_date
        if self.birth_date:
            today = datetime.date.today()
            birth_date = self.birth_date.date()  # convert datetime to date if needed
            self.age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )
        else:
            self.age = None

        # Calculate BFP using BMI + age + gender
        if self.bmi is not None and self.age is not None:
            if self.gender == self.MAN:
                self.bfp = round((1.20 * self.bmi) + (0.23 * self.age) - 16.2, 1)
            elif self.gender == self.WOMAN:
                self.bfp = round((1.20 * self.bmi) + (0.23 * self.age) - 5.4, 1)

        super().save(*args, **kwargs)

    def predict_cycle_phase(self):
        """
        Sends a POST request to /phase-predict to get predicted menstrual phase.
        Saves the result to `cycle_record_json`.
        """
        
        # Prepare input data
        try:
            payload = {
                "age": int(self.age) if self.age else 0,
                "height_cm": float(self.height.height) if self.height else 0,
                "weight_kg": float(self.weight.weight) if self.weight else 0,
                "bmi": float(self.bmi) if self.bmi else 0,
                "bfp": float(self.bfp) if self.bfp else 0,
                "cycle_day": int(self.cycle_day) if self.cycle_day else 0,
                "cycle_length": int(self.cycle_length) if self.cycle_length else 0,
            }
            # Send POST request
            url = "http://host.docker.internal:8000/phase/predict"
            response = requests.post(url, json=payload)

            # Handle success
            if response.status_code == 200:
                try:
                    result = response.json()
                    predicted_phase = result.get("predicted_phase", str())
                    if predicted_phase:
                        self.menstrual_phase = predicted_phase
                    self.cycle_record_json = result
                    self.save(update_fields=["cycle_record_json", "menstrual_phase"])
                    return result
                except ValueError:
                    # Invalid JSON returned
                    self.cycle_record_json = {"error": "Invalid response format"}
                    self.save(update_fields=["cycle_record_json"])
                    return None
            else:
                # Save error response
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"error": "Unknown server error"}
                self.cycle_record_json = {"error": error_data}
                self.save(update_fields=["cycle_record_json"])
                return error_data

        except Exception as e:
            # General error fallback
            self.cycle_record_json = {"error": str(e)}
            self.save(update_fields=["cycle_record_json"])
            return {"error": str(e)}
