__all__ = ()

from http import HTTPStatus

from django.contrib.auth import login
from django.db import transaction
from rest_framework import generics, permissions
from rest_framework.response import Response

from users import serializers
from users.models import User


class LoginView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = User.normalize_phone(serializer.data[User.phone.field.name])
        with transaction.atomic():
            user = User.objects.get_or_create(phone=phone)[0]

        user.handle_confirmation_login()
        return Response({'status': 'ok'})


class LoginConfirmView(generics.GenericAPIView):
    serializer_class = serializers.LoginConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        user = User.check_confirmation_login_code(code)
        if not user:
            return Response(
                {'status': "code isn't correct"},
                HTTPStatus.BAD_REQUEST,
            )

        login(request, user)
        return Response({'status': 'authenticated'})


class ProfileView(generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = serializers.ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
