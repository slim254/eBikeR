from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from utils.logging import get_logger, log_api_request, log_api_response, log_api_error, log_user_action, log_business_event

from utils.response import api_response
from utils.authentication import OptionalJWTAuthentication
from .serializers import (
    SignupSerializer, 
    UserSerializer, 
    UserUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

logger = get_logger("users")


class SignupAPIView(APIView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        log_api_request(logger, request, "user_signup", user_data=request.data)
        
        try:
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                log_business_event(logger, "user_registered", user_id=str(user.id), 
                                 user_email=user.email)
                
                response = api_response(
                    success=True,
                    message="User created successfully",
                    data=serializer.data,
                    status_code=status.HTTP_201_CREATED,
                )
                log_api_response(logger, request, "user_signup", status.HTTP_201_CREATED, 
                               user_id=str(user.id))
                return response
            
            log_api_response(logger, request, "user_signup", status.HTTP_400_BAD_REQUEST, 
                           validation_errors=serializer.errors)
            return api_response(
                success=False,
                message="User creation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log_api_error(logger, request, "user_signup", e)
            raise


class LoginAPIView(TokenObtainPairView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        log_api_request(logger, request, "user_login", login_data=request.data)
        
        try:
            serializer = self.get_serializer(data=request.data)

            if not serializer.is_valid():
                log_api_response(logger, request, "user_login", status.HTTP_400_BAD_REQUEST, 
                               validation_errors=serializer.errors)
                return api_response(
                    success=False,
                    message="Login failed",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            response = api_response(
                success=True,
                message="Login successful",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK,
            )
            
            # Log successful login
            user = serializer.user if hasattr(serializer, 'user') else None
            if user:
                log_business_event(logger, "user_login", user_id=str(user.id), 
                                 user_email=user.email)
            
            log_api_response(logger, request, "user_login", status.HTTP_200_OK, 
                           user_id=str(user.id) if user else None)
            return response
        except Exception as e:
            log_api_error(logger, request, "user_login", e)
            raise


class TokenRefreshAPIView(TokenRefreshView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return api_response(
                success=False,
                message="Token refresh failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return api_response(
            success=True,
            message="Token refreshed successfully",
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK,
        )


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        log_api_request(logger, request, "get_user_profile")
        
        try:
            serializer = UserSerializer(request.user)
            response = api_response(
                success=True,
                message="User fetched successfully",
                data=serializer.data,
            )
            log_api_response(logger, request, "get_user_profile", status.HTTP_200_OK, 
                           user_id=str(request.user.id))
            return response
        except Exception as e:
            log_api_error(logger, request, "get_user_profile", e)
            raise
    
    def put(self, request):
        """Update user profile."""
        log_api_request(logger, request, "update_user_profile", update_data=request.data)
        
        try:
            serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                log_user_action(logger, request, "update_profile", resource_id=str(request.user.id))
                
                # Return updated user data
                user_serializer = UserSerializer(request.user)
                response = api_response(
                    success=True,
                    message="Profile updated successfully",
                    data=user_serializer.data,
                )
                log_api_response(logger, request, "update_user_profile", status.HTTP_200_OK, 
                               user_id=str(request.user.id))
                return response
            
            log_api_response(logger, request, "update_user_profile", status.HTTP_400_BAD_REQUEST, 
                           validation_errors=serializer.errors)
            return api_response(
                success=False,
                message="Profile update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            log_api_error(logger, request, "update_user_profile", e)
            raise
    
    def patch(self, request):
        """Partially update user profile."""
        return self.put(request)


class PasswordResetRequestAPIView(APIView):
    """Request password reset email."""
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                success=True,
                message="If an account with this email exists, a password reset link has been sent.",
                data=None,
                status_code=status.HTTP_200_OK,
            )
        return api_response(
            success=False,
            message="Invalid email address",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetConfirmAPIView(APIView):
    """Confirm password reset with token."""
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, uid, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # Validate token and uid
            try:
                user = serializer.validate_token_and_uid(uid, token)
                serializer.save()
                return api_response(
                    success=True,
                    message="Password has been reset successfully",
                    data=None,
                    status_code=status.HTTP_200_OK,
                )
            except Exception as e:
                return api_response(
                    success=False,
                    message=str(e),
                    data=None,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        return api_response(
            success=False,
            message="Invalid data",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
