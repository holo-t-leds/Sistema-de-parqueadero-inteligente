from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RoleTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class RoleTokenObtainPairView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer


class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            {
                'id': request.user.id,
                'username': request.user.get_username(),
                'email': request.user.email,
                'role': 'admin' if request.user.is_staff else 'cliente',
            }
        )
