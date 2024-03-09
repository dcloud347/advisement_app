from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError('用户名或密码错误')
        if not user.is_active:
            raise ValidationError('用户已被禁用')
        login(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        logout(self.request)
        return Response(status=HTTP_200_OK)