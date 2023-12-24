from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegisterSerializer, UserDetailSerializer, VerifyCodeSerializer, UserDescSerializer
from .serializers import CustomUserTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from .permissions import IsSelfOrReadOnly
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, VerifyEmail
from .utils import SendCodeEmail, generate_code
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserRegisterSerializer
    lookup_field = 'username'
    queryset = CustomUser.objects.all()

    @action(detail=True, methods=['get'])
    def info(self, request, username=None):
        queryset = CustomUser.objects.get(username=username)
        serializer = UserDetailSerializer(queryset, many=False)
        return Response(serializer.data)

    @action(detail=False)
    def sorted(self, request):
        users = CustomUser.objects.all().order_by('-username')
        page = self.paginate_queryset(users)
        if page is None:
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserDescSerializer
        elif self.action == 'create':
            return UserRegisterSerializer
        else:
            return UserDescSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsSelfOrReadOnly, IsAuthenticatedOrReadOnly]
        return super().get_permissions()


class CustomUserTokenPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserTokenSerializer


class CustomBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except ObjectDoesNotExist as e:
            return None


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_verify_code(request):
    if request.method == 'POST':
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True) and serializer.validated_email(request.data.get('email')):
            email = serializer.validated_data.get('email')
            code = generate_code()

            sms_status = SendCodeEmail.send_email_code(code=code, to_email_address=email)
            if sms_status == 0:
                return Response({'msg': '邮件发送失败'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                code_recode = VerifyEmail(code=code, email=email)
                code_recode.save()
                return Response({'msg': '验证码已发送'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
