from django.contrib.auth import authenticate, logout
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Account, Activity, Group
from .serializers import (
    AccountRegisterSerializer,
    AccountSerializer,
    ActivitySerializer,
    GroupSerializer,
    SendResetCodeSerializer,
    UserLoginSerializer,
    UserResetPasswordSetPasswordSerializer,
    get_token,
)
from apps.utils.email import send_email
from apps.utils.serializers import EmptySerializer
from apps.utils.sms import send_sms
from apps.utils.permissions import IsAccount, IsRegisterEnabled


class AccountAuthViewSet(viewsets.GenericViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.filter(deleted=False)
    permission_classes = [
        IsAuthenticated,
        IsAccount,
    ]

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny, IsRegisterEnabled],
        serializer_class=AccountRegisterSerializer,
    )
    def register(self, request):
        serializer = self.serializer_class(data=request.data)
        data = dict()
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = serializer.data
            if request.data.get("authenticate"):
                user = authenticate(
                    username=data.get("email"),
                    password=request.data.get("raw_password"),
                )
                token = get_token(user)
                data["token"] = token.key
        return Response(data)

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=UserLoginSerializer,
    )
    def login(self, request):
        """User sign in."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        return Response({"user": user, "token": token})

    @action(detail=False, methods=["POST"], serializer_class=EmptySerializer)
    def logout(self, request):
        """User sign out"""
        token = Token.objects.filter(user=request.user.id).first()
        logout(request)
        if token:
            token.delete()
        return Response({"success": True})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SendResetCodeSerializer,
    )
    def send_reset_code(self, request):
        email = request.data.get("email")
        user = get_object_or_404(Account, username=email)
        user.generate_reset_password_code()
        sending_method = request.data.get("sending_method")
        success = True
        if sending_method == "sms":
            data = send_sms(
                "+573022327626",
                f"Tu código de verificación es {user.reset_password_code}",
            )
        elif sending_method == "email":
            template = "Tu código de verificación es {{ code }}"
            context = {"code": user.reset_password_code}
            data = send_email("Reiniciar contraseña", email, template, context)
        else:
            success = False
            data = "Missing or wrong parameter"
        return Response({"success": success, "data": data})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=UserResetPasswordSetPasswordSerializer,
    )
    def set_new_password(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        password = request.data.get("password")
        user = get_object_or_404(Account, username=email, reset_password_code=code)
        if all((email, code, password)):
            user.reset_password(password)
            success = True
        else:
            success = False
        return Response({"success": success})

    @action(detail=False, methods=["GET"])
    def detail_user(self, request):
        serializer = self.serializer_class(request.user.account)
        return Response(serializer.data)

    @action(detail=False, methods=["PUT"])
    def update_user(self, request):
        serializer = self.serializer_class(request.user.account, request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.filter(deleted=False)


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.filter(deleted=False)
