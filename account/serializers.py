import re
from datetime import datetime, timedelta
from rest_framework import serializers
from .models import CustomUser, VerifyEmail
from django.utils import timezone
from django.core.validators import RegexValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

phone_validator = RegexValidator(
    regex=r'^(1[3-9])\d{9}',
    message='非法号码。'
)
EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


class VerifyCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    # phone = serializers.CharField(validators=phone_validator,)

    def validated_email(self, email):
        if CustomUser.objects.filter(email=email).count():
            raise serializers.ValidationError('该邮箱已注册')
        if not re.match(EMAIL_REGEX, email):
            raise serializers.ValidationError('邮箱格式错误')
        one_minute_age = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyEmail.objects.filter(add_time__gt=one_minute_age, email=email):
            raise serializers.ValidationError('请一分钟后再试')
        return email

    class Meta:
        model = VerifyEmail
        fields = ['email', 'code']


class UserDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'last_login', 'date_joined']


class UserRegisterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='customuser-detail', lookup_field='username')

    code = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=6,
        max_length=6,
        help_text='验证码',
        error_messages={
            'blank': '请输入验证码',
            'required': '请输入验证码',
            'min_length': '验证码格式错误',
            'max_length': '验证码格式错误', },
        write_only=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['url', 'id', 'email', 'username', 'code', 'password', 'is_superuser', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser': {'read_only': True},
        }

    def validate_code(self, code):
        verify_recode = VerifyEmail.objects.filter(email=self.initial_data['email']).order_by('-add_time')
        if verify_recode:
            last_recode = verify_recode[0]
            five_minutes_age = timezone.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_minutes_age > last_recode.add_time:
                raise serializers.ValidationError('验证码过期')
            if last_recode.code != code:
                raise serializers.ValidationError('验证码错误')
        else:
            raise serializers.ValidationError('验证码不存在')

    def validate(self, attrs):
        del attrs['code']
        password1 = attrs.get('password')
        password2 = attrs.get('password2')

        if password1 != password2:
            raise serializers.ValidationError('两个密码不匹配')

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'username',
                  'last_name',
                  'first_name',
                  'email',
                  'last_login',
                  'date_joined',
                  'phone',
                  'is_superuser',
                  ]

class CustomUserTokenSerializer(TokenObtainPairSerializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.username
        token['email'] = user.email
        token['nickname'] = user.nickname
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['token'] = data.get('access')
        del data['access']
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data