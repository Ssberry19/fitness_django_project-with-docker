from datetime import datetime
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.models import User
from users.models import HeightModel, WeightModel, Allergen

activity_levels = {
    1: "sedentary",
    2: "light",
    3: "moderate",
    4: "high",
    5: "extreme",
}
activity_levels_2 = {
    "sedentary": 1,
    "light": 2,
    "moderate": 3,
    "high": 4,
    "extreme": 5,
}
goals = {1: "weightLoss", 2: "weightGain", 3: "maintenance"}
goals_2 = {"loseWeight": 1, "gainWeight": 2, "maintain": 3}


class CreateUpdateUserView(APIView):
    """Create user"""

    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        data = request.data
        print("CreateUpdateUserView. data: ", data)

        username = data.get("username")
        password = data.get("password")
        birth_date = data.get("birthDate")

        if birth_date:
            birth_date_dt = datetime.fromisoformat(birth_date)

        email = data.get("email")

        if data.get("gender") == "male":
            gender = User.MAN
        else:
            gender = User.WOMAN

        goal = goals_2.get(data.get("goal", ""), 1)
        target_weight = data.get("targetWeight", 70)

        # cycles
        if data.get("cycleDay", 0):
            cycle_day = int(data.get("cycleDay", 0))
        else:
            cycle_day = None

        if data.get("cycleLength"):
            cycle_length = int(data.get("cycleLength", 0))
        else:
            cycle_length = None

        last_period_date = data.get("lastPeriodDate")
        if last_period_date:
            last_period_date_dt = datetime.fromisoformat(last_period_date)
        else:
            last_period_date_dt = None

        try:
            User.objects.create(
                username=username,
                birth_date=birth_date_dt,
                email=email,
                gender=gender,
                target_weight=target_weight,
                goal=goal,
                activity_level=activity_levels_2.get(data.get("activityLevel"), 1),
                cycle_length=cycle_length,
                cycle_day=cycle_day,
                last_period_date=last_period_date_dt,
            )
        except IntegrityError:
            print("users create error exception traceback")
            import traceback

            print(traceback.print_exc())
            return Response("Integrity error", status=400)

        user = None
        for val in get_user_model().objects.all():
            if val.email == email:
                user = val
                break

        allergens = data.get("allergens", [])
        if allergens:
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

        if user.gender == User.WOMAN:
            user.predict_cycle_phase()

        token = Token.objects.create(user=user)
        return Response({"token": token.key}, status=200)


class LoginUserView(APIView):
    """Create user"""

    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        data = request.data
        print("LoginUserView. data: ", data)

        email = data.get("email")
        users = get_user_model().objects.all()
        for user in users:
            if user.email == email:
                target_user = user
                break
        else:
            return Response("No user", status=404)

        user = authenticate(
            request=request,
            username=email,
            password=data.get("password"),
        )
        if user is None:
            return Response("invalid login", status=200)

        old_token = Token.objects.filter(user=target_user)
        if old_token:
            old_token.delete()

        token = Token.objects.create(user=target_user)
        target_user.save()

        if target_user.gender == User.WOMAN:
            target_user.predict_cycle_phase()

        return Response({"token": token.key}, status=200)


class ProfileInfoView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print("ProfileInfoView. user: ", request.user)
        weight = user.weight
        height = user.height
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
                "activityLevel": activity_levels.get(user.activity_level, "sedentary"),
                "targetWeight": user.target_weight,
                "goal": goals.get(user.goal, "loseWeight"),
                "menstrualCycles": [],
                "menstrualPhase": user.menstrual_phase,
                "cycleDay": user.cycle_day,
                "cycleLength": user.cycle_length,
                "lastPeriodDate": user.last_period_date,
                "age": user.age,
                "bmi": user.bmi,
                "bmf": user.bmf,
            },
        }

        return Response(result, status=200)


class WeightHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        print("WeightHistoryView. user: ", user)
        weights = WeightModel.objects.filter(user=user)
        weights_list = [
            {str(weight.weight): weight.updated_at.strftime("%Y-%m-%d")}
            for weight in weights
        ]
        return Response(weights_list, status=200)


class LogoutUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print("LogoutUserView: ", request.user)
        old_token = Token.objects.filter(user=user)
        if old_token:
            old_token.delete()
        return Response("Successfully logout", status=200)


class UpdateUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        print("UpdateUserView. user: ", user)
        print("UpdateUserView. data: ", data)

        if data.get("username"):
            user.username = data.get("username")

        birth_date = data.get("birthDate")
        if birth_date:
            birth_date_dt = datetime.fromisoformat(birth_date)
            user.birth_date = birth_date_dt

        if data.get("email"):
            user.email = data.get("email")

        if data.get("targetWeight"):
            user.target_weight = data.get("targetWeight")

        if data.get("gender") == "male":
            gender = User.MAN
        else:
            gender = User.WOMAN

        if gender:
            user.gender = gender

        goal = goals_2.get(data.get("goal", ""), 1)
        if goal:
            user.goal = goal

        activity_level = activity_levels_2(data.get("activityLevel", ""), 1)
        if activity_level:
            user.activity_level = activity_level

        if data.get("cycleDay", 0):
            cycle_day = int(data.get("cycleDay", 0))
        else:
            cycle_day = None

        if cycle_day:
            user.cycle_day = cycle_day

        if data.get("cycleLength"):
            cycle_length = int(data.get("cycleLength", 0))
        else:
            cycle_length = None

        if cycle_length:
            user.cycle_length = cycle_length

        last_period_date = data.get("lastPeriodDate")
        if last_period_date:
            last_period_date_dt = datetime.fromisoformat(last_period_date)
        else:
            last_period_date_dt = None

        if last_period_date_dt:
            user.last_period_date = last_period_date_dt

        allergens = data.get("allergens", [])
        if allergens:
            for allergen in allergens:
                allergen_value = Allergen.objects.get(name=allergen)
                user.allergens.add(allergen_value)

        height = data.get("height", 175)
        if height:
            height = HeightModel(height=height, user=user)
            height.save()

        weight = data.get("weight", 80)
        if weight:
            weight = WeightModel(weight=weight, user=user)
            weight.save()

        user.weight = weight
        user.height = height

        password = data.get("password")
        user.set_password(password)
        user.save()

        return Response({"status": "success"}, status=200)


class PredictCyclePhaseView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print("PredictCyclePhaseView. user: ", user)
        user.predict_cycle_phase()
        result = user.cycle_record_json
        return Response(result, status=200)
