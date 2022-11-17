from django.contrib.auth import authenticate, logout
from rest_framework import mixins, viewsets
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
from apps.utils.choices import ROLES
from apps.utils.constants import ACTIVITY_CATEGORIES, ACTIVITY_STATUSES
from apps.utils.email import send_email
from apps.utils.serializers import EmptySerializer
from apps.utils.sms import send_sms
from apps.utils.permissions import IsAccount, IsRegisterEnabled
from apps.utils.viewsets import CustomPagination


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

    @action(detail=False, methods=["PUT"])
    def update_user(self, request):
        serializer = self.serializer_class(request.user.account, request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class ActivityViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Activity.objects.filter(deleted=False).order_by("-start_date")
    serializer_class = ActivitySerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(group=request.user.account)
        result_page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(result_page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        if request.user.is_staff or request.user.account == instance.group.account:
            serializer = self.get_serializer(instance)
            data = serializer.data
            data["start_date"] = instance.start_date.strftime("%Y-%m-%d %H:%M")
            data["end_date"] = instance.end_date.strftime("%Y-%m-%d %H:%M")
            data["group"] = instance.group.name
            data["status"] = (instance.status, instance.get_status_display())
            return Response(data)
        return Response({"detail": "Not found."}, status=404)

    @action(detail=False, methods=["GET"])
    def constants(self, request):
        return Response(
            {
                "categories": ACTIVITY_CATEGORIES,
                "statuses": ACTIVITY_STATUSES,
            }
        )


class GroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = GroupSerializer
    queryset = Group.objects.filter(deleted=False)


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def list(self, request):
        data = request.GET
        role = data.get("role", [r[0] for r in ROLES])
        if type(role) is str:
            role = role.split(",")
        queryset = Account.objects.filter(role__in=role)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
