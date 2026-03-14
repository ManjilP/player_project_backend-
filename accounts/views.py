import random
from datetime import timedelta

from accounts.serializers import (
       LoginSerializer,
       ChangePasswordSerializer,
       RegisterUserSerializer,
       EditUserSerializer,
   )

from accounts.models import User, InvitedManager
from accounts.tasks import send_otp_mail, send_manager_invitation_mail

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import login
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes


from knox import views as knox_views


class LoginAPIView(knox_views.LoginView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            is_superuser = user.is_superuser
            response = super().post(request, format=None)
            response.data['role'] = user.role
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            response.data,
            status=status.HTTP_200_OK
        )
    

class ForgotPasswordRequestAPIView(generics.CreateAPIView):

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.only('otp', 'otp_expiry').get(email=email)

            user.otp = random.randint(100000, 999999)
            user.otp_expiry = timezone.now() + timedelta(minutes=5)
            user.save()

            reset_link = reverse('accounts:validate_otp')
            reset_url = f"{request.scheme}://{request.get_host()}{reset_link}"

            send_otp_mail.delay(email, user.otp, user.otp_expiry, user.name, reset_url)

            return Response(
                {
                    'message': f'Your OTP is sent to {email}. This One Time password is valid until {user.otp_expiry}!',
                    'reset_link': reset_url
                },
                status= status.HTTP_200_OK
            )
        
        except User.DoesNotExist:
            return Response(
                {'message': 'User with the provided mail doesn\'t exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class ValidateOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)

            if user.otp is None and user.otp_expiry is None:
                return Response(
                    {'message': 'No OTP is generated or OTP has expired!'},
                    status = status.HTTP_400_BAD_REQUEST
                )
            
            if timezone.now() > user.otp_expiry:
                user.otp = None
                user.otp_expiry = None
                user.save()
                return Response(
                    {'message': 'OTP has expired!'},
                    status= status.HTTP_400_BAD_REQUEST
                )
            
            if str(user.otp) == str(otp):
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = f"{request.scheme}://{request.get_host()}/accounts/password/reset/{uid}/{token}/"
                
                return Response(
                    {
                        'message': 'OTP is valid. Please use the reset URL to change your password.',
                        'reset_url': reset_url
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({'message': 'OTP is not correct.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({'message': 'No OTP found!'}, status=status.HTTP_400_BAD_REQUEST) 


class ResetPasswordView(APIView):
    def post(self, request, uid, token):
        
        pk = urlsafe_base64_decode(uid).decode()
        try:
            user = User.objects.get(pk=pk)

            if not default_token_generator.check_token(user, token):
                return Response(
                    {
                        'message': 'Token is invalid or Expired!'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                new_password = request.data.get('new_password')
                confirm_password = request.data.get('confirm_password')

                if new_password != confirm_password:
                    return Response(
                        {'message': 'Passwords don\'t match!'},
                        status= status.HTTP_400_BAD_REQUEST
                    )
                
                user.set_password(new_password)
                user.otp = None
                user.otp_expiry = None
                user.save()

                return Response(
                    {'message': 'Your Password has been reset successfully!'},
                    status= status.HTTP_200_OK
                )
        
        except ObjectDoesNotExist:
            return Response(
                {'message': 'User does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            user = request.user
            new_password = serializer.validated_data.get('new_password')

            user.set_password(new_password)
            user.save()

            return Response(
                {'message': "Password Changed Successfully!"},
                status = status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class UserRegisterCreateAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['role'] = "PLAYER"

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': "User created successfully!",
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class InviteNewManagerAPIView(generics.GenericAPIView):
    permission_classes = (IsAdminUser,)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        name = request.POST.get('name')

        if User.objects.filter(email=email).exists():
            return Response(
                {
                    'message': "User with this email already exists!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            encoded_email = urlsafe_base64_encode(force_bytes(email))
            registration_url = f"{request.scheme}://{request.get_host()}/accounts/register/manager/invited/{encoded_email}/"

            send_manager_invitation_mail.delay(email, name, registration_url)

            invited_manager, created = InvitedManager.objects.get_or_create(email=email)
            invited_manager.expiry = timezone.now() + timedelta(hours=1)
            invited_manager.save()


            return Response(
                {
                    'message': "Invitation created!",
                    "registration_link": registration_url
                },
                status=status.HTTP_201_CREATED
            )
        

class RegisterInvitedManagerAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    def post(self, request, encoded_email, *args, **kwargs):
        email = urlsafe_base64_decode(encoded_email).decode()

        if User.objects.filter(email=email).exists():
            return Response(
                {
                    'message': "User with this email already exists!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            try:
                invited_manager = InvitedManager.objects.get(email=email)
            except InvitedManager.DoesNotExist:
                return Response(
                    {
                        'message': "You haven't been invited!"
                    },
                    status= status.HTTP_400_BAD_REQUEST
                )     
            
            if invited_manager.expiry < timezone.now(): # type: ignore
                return Response(
                    {'message': "The link has already been expired!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = request.data.copy()
            data['email'] = email
            data['role'] = "MANAGER"

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                user.is_staff = True

                invited_manager.delete()

                return Response(
                    {
                        'message': "User Created Succesfully!",
                        'data': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class EditProfileAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditUserSerializer

    def patch(self, request, *args, **kwargs):
        user = request.user
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': "User Updated Successfully!",
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )