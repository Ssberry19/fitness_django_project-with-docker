from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin, User
from django.conf import settings


class HeightModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Рост", null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменено")

    def __str__(self):
        return str(self.height)


class WeightModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Вес", null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменено")

    def __str__(self):
        return str(self.weight)


class CycleModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")


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
    """
    **Parameters:**
        - `gender`: String, either "M" or "F"
        - `age`: Integer, age in years
        - `height`: Float, height in cm
        - `weight`: Float, weight in kg
        - `goal`: String, one of "weight_loss", "maintenance", "weight_gain", "cutting"
        - `activity_level`: String, one of "sedentary", "light_activity", "moderate_activity", "very_active"
        - `target_weight`: Float, target weight in kg (optional)
        - `cycle_start_date`: String, date of last menstrual cycle start in YYYY-MM-DD format (optional, for women only)

        пол, рост, возраст, вес (соотвественно сразу формула ИМТ), цель (похудение, поддержание тонуса, набор веса, сушка), целевой вес (прогнозируемое ИМТ), уровень активности (сидячий, легкая активность, умеренная активность, очень активный), даты начала последних трех циклов (для женщин) для определения фаз (менструальной, фолликулярной, овуляторной и лютеиновой фазы)
    """

    MAN = 1
    WOMAN = 2
    GENDERS = [
        (MAN, "Мужчина"),
        (WOMAN, "Женщина"),
    ]

    WEIGHT_LOSS = 1
    WEIGHT_GAIN = 2
    MAINTENANCE = 3
    GOALS = [
        (WEIGHT_LOSS, "Похудение"),
        (WEIGHT_GAIN, "Набор массы"),
        (MAINTENANCE, "Тонус"),
    ]

    SEDENTARY = 1
    LIGHT = 2
    MODERATE = 3
    HIGH = 4
    EXTREME = 5
    ACTIVITY_LEVELS = [
        (SEDENTARY, "Сидячий"),
        (LIGHT, "Легкая активность"),
        (MODERATE, "Умеренная активность"),
        (HIGH, "Высокая активность"),
        (EXTREME, "Очень высокая активность"),
    ]

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Администратор")
    full_name = models.CharField(max_length=255, null=True)
    birth_date = models.CharField(max_length=255, null=True)
    age = models.IntegerField(verbose_name="Возраст")
    gender = models.IntegerField(choices=GENDERS, verbose_name="Пол")
    email = models.CharField(max_length=255, null=True, unique=True)
    height = models.ForeignKey(
        HeightModel,
        on_delete=models.CASCADE,
        related_name="Рост",
        verbose_name="Рост",
        null=True,
        blank=True,
    )
    weight = models.ForeignKey(
        WeightModel,
        on_delete=models.CASCADE,
        related_name="Вес",
        verbose_name="Вес",
        null=True,
        blank=True,
    )
    target_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Целевой вес"
    )
    goal = models.IntegerField(choices=GOALS, verbose_name="Цель")
    activity_level = models.IntegerField(
        choices=ACTIVITY_LEVELS, verbose_name="Уровень активности"
    )
    cycle_record = models.ForeignKey(
        CycleModel,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="Цикл",
        verbose_name="Цикл",
    )
    """
        int? cycleLength; // Длина цикла
        DateTime? lastPeriodDate; // Дата последней менструации
        int? cycleDay;
    """
    cycle_length = models.IntegerField(
        null=True, blank=True, verbose_name="Длина цикла в днях"
    )
    last_period_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата последней менструации"
    )
    cycle_day = models.IntegerField(
        null=True, blank=True, verbose_name="День текущего цикла"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Изменено")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_bmi(self, weight, height):
        bmi = weight / (height * height)
        return bmi
