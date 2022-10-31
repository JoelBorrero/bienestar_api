from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Account, Activity, Group
from apps.utils.exceptions import EmailValidationError
from apps.utils.shortcuts import get_object_or_none


def get_token(user):
    token = get_object_or_none(Token, user=user)
    if token:
        token.delete()
    token = Token.objects.create(user=user)
    return token


class SendResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    sending_method = serializers.CharField(max_length=5, default='sms', help_text='sms or email')

    def validate(self, data):
        if Account.objects.filter(username=data.get('email')):
            raise EmailValidationError()
        return data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class EmptySerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserResetPasswordCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class UserResetPasswordSetPasswordSerializer(UserResetPasswordCodeSerializer):
    password = serializers.CharField(min_length=6)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        user = authenticate(username=data.get('email'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError({
                'error': 'Las credenciales no son válidas'
            })
        if not hasattr(user, 'account'):
            raise serializers.ValidationError({
                'error': 'No tiene permisos para entrar aquí'
            })
        self.context['user'] = user
        return data

    def create(self, data):
        user = self.context['user']
        token = get_token(user)
        user = AccountSerializer(user.account)
        return user.data, token.key


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active'
        )


class AccountRegisterSerializer(AccountSerializer):
    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ('raw_password',)
        extra_kwargs = {
            'raw_password': {
                'write_only': True
            },
            'role': {
                'read_only': True
            },
            'code': {
                'read_only': True
            },
            'is_active': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        instance = super().create(validated_data)
        return instance


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = (
            'pk',
            'ext_id',
            'name',
            'description',
            'group',
        )
        depth = 1


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            'name',
            'description',
            'email',
            'is_active'
        )
