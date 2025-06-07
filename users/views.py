from datetime import date
from datetime import datetime

from django.utils.crypto import get_random_string
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.models import User
from users.models import HeightModel, WeightModel, Allergen

# full_name
# gender
# email
# birthDate
# weight
# height
# activity level
# target_weight
# goal


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class CreateUpdateUserView(APIView):
    """Create user"""

    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        """
              String? fullName;
        Gender? gender;
        DateTime? birthDate;
        double? height;
        double? weight;
        double? targetWeight;
        FitnessGoal? goal;
        ActivityLevel? activityLevel;
        int? cycleLength; // Длина цикла
        DateTime? lastPeriodDate; // Дата последней менструации
        int? cycleDay;
        String? email;
        String? password;
        """

        """
        {
        'fullName': 'ubsa',
        'gender': 'female',
        'birthDate': '2025-05-21T00:00:00.000',
        'height': 170.0,
        'weight': 85.0,
        'targetWeight': 65.0,
        'goal': 'loseWeight',
        'activityLevel': None,
        'menstrualCycles': ['2025-05-14T00:00:00.000Z', '2025-04-16T00:00:00.000Z', '2025-03-12T00:00:00.000Z'],
        'email': 'insaniyatka@gmail.com',
        'password': 'insA10!'
        }
        """

        activity_level_2 = {
            "sedentary": 1,
            "light": 2,
            "moderate": 3,
            "high": 4,
            "extreme": 5,
        }

        """
            GOALS = [
            (WEIGHT_LOSS, "Похудение"),
            (MAINTENANCE, "Тонус"),
            (WEIGHT_GAIN, "Набор массы"),
            (CUTTING, "Сушка"),
            ]
        """
        goals_2 = {"loseWeight": 1, "gainWeight": 2, "maintain": 3}

        data = request.data
        print("data: ", data)

        username = data.get("username")
        password = data.get("password")
        birth_date = data.get("birthDate")

        if birth_date:
            birth_date_dt = datetime.fromisoformat(birth_date)
            age = calculate_age(birth_date_dt)
        else:
            age = 1

        email = data.get("email")

        if data.get("gender") == "male":
            gender = User.MAN
        else:
            gender = User.WOMAN

        goal = goals_2.get(data.get("goal", ""), 1)
        target_weight = data.get("targetWeight", 70)

        # cycles
        cycle_day = int(data.get("cycleDay", 0))
        cycle_length = int(data.get("cycleLength", 0))
        last_period_date = data.get("lastPeriodDate")

        if last_period_date:
            last_period_date_dt = datetime.fromisoformat(last_period_date)
        else:
            last_period_date_dt = None

        try:
            User.objects.create(
                username=username,
                birth_date=birth_date,
                age=age,
                email=email,
                gender=gender,
                # height=height,
                # weight=weight,
                target_weight=target_weight,
                goal=goal,
                activity_level=activity_level_2.get(data.get("activityLevel"), 1),
                cycle_record=None,
                cycle_length=cycle_length,
                cycle_day=cycle_day,
                last_period_date=last_period_date_dt,
            )
        except IntegrityError:
            import traceback

            print(traceback.print_exc())

            return Response("Integrity error", status=400)

        user = None
        for val in get_user_model().objects.all():
            print(repr(val.email))
            if val.email == email:
                user = val
                break

        allergens = data.get("allergens")
        for allergen in allergens:
            allergen_value = Allergen.objects.get(name=allergen)
            user.allergens.add(allergen_value)

        height = data.get("height", 175)
        height = HeightModel(height=height, user=user)
        height.save()

        weight = data.get("weight", 80)
        weight = WeightModel(weight=weight, user=user)
        weight.save()

        user.weight = weight
        user.height = height
        user.set_password(password)
        user.save()

        token = Token.objects.create(user=user)
        print(token.key)

        return Response({"token": token.key}, status=200)


class LoginUserView(APIView):
    """Create user"""

    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        data = request.data
        print("login user view enter: ", data)
        email = data.get("email")

        users = get_user_model().objects.all()
        for user in users:
            if user.email == email:
                target_user = user
                break
        else:
            return Response("No user", status=404)

        print("username: ", target_user.username)
        print("password: ", data.get("password"))

        user = authenticate(
            request=request,
            username=email,
            password=data.get("password"),
        )
        print("user: ", user)
        if user is None:
            return Response("invalid login", status=200)

        old_token = Token.objects.filter(user=target_user)
        if old_token:
            old_token.delete()

        print("target user: ", target_user)
        token = Token.objects.create(user=target_user)
        print(token.key)

        return Response({"token": token.key}, status=200)


class ProfileInfoView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = [Tpl]  # Allow public access to model information

    def post(self, request):
        user = request.user
        print("user: ", request.user)
        print("auth: ", request.auth)
        activity_level = {
            1: "sedentary",
            2: "light",
            3: "moderate",
            4: "high",
            5: "extreme",
        }
        goals = {1: "weightLoss", 2: "weightGain", 3: "maintenance"}

        data = request.data
        print("data: ", data)

        weight = user.weight
        height = user.height
        print("weight: ", weight)

        result = {
            "status": "okay",
            "message": "zaebis",
            "data": {
                "username": user.username,
                "gender": "male" if user.gender == 1 else "female",
                "email": user.email,
                "birthDate": user.birth_date,
                "weight": weight.weight,
                "height": height.height,
                "activityLevel": activity_level.get(user.activity_level, "sedentary"),
                "targetWeight": user.target_weight,
                "goal": goals.get(user.goal, "loseWeight"),
                "menstrualCycles": [],
                "cycleDay": user.cycle_day,
                "cycleLength": user.cycle_length,
                "lastPeriodDate": user.last_period_date,
            },
        }

        return Response(result, status=200)


class WeightHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        data = request.data
        print("data: ", data)

        email = data.get("email")
        print("repr: ", repr(email))

        if email:
            print("iser odL ", email)
            for val in get_user_model().objects.all():
                print(repr(val.email))
                if val.email == email:
                    user = val
                    break
            else:
                return Response(status=404)
        else:
            user = get_user_model().objects.last()

        print("user: ", user)
        weights = WeightModel.objects.filter(user=user)

        print("user weights: ", weights)
        for weight in weights:
            print("weight: ", weight)
        weights_list = [
            {str(weight.weight): weight.updated_at.strftime("%Y-%m-%d")}
            for weight in weights
        ]
        return Response(weights_list)


class LogoutUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print("logout: ", request.user)
        old_token = Token.objects.filter(user=user)
        if old_token:
            old_token.delete()
        return Response("Successfully logout", status=200)
