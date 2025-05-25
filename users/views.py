from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from users.models import User
from users.models import HeightModel, WeightModel


class CreateUpdateUserView(APIView):
    """Create user"""

    permission_classes = [AllowAny]  # Allow public access to model information

    def post(self, request):
        data = request.data
        print("data: ", data)
        
        user_id = get_random_string(12)
        
        height = data.get("height", 175)
        height = HeightModel(height=height)
        height.save()

        weight = data.get("weight", 80)
        weight = WeightModel(weight=weight)
        weight.save()

        target_weight = data.get("target_weight", 70)

        User.objects.create(
            user_id=user_id,
            age=28,
            gender=User.MAN,
            height=height,
            weight=weight,
            target_weight=target_weight,
            goal=User.WEIGHT_GAIN,
            activity_level=User.MODERATE_ACTIVITY,
            cycle_record=None,
        )

        return Response()


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})
