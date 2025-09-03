from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserRegisterSerializer, UserSerializer


# -------------------------
# Custom JWT authentication for cookies
# -------------------------
class CookiesJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        return super().authenticate(request)


# -------------------------
# User Registration (public)
# -------------------------
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])  # no auth
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


# -------------------------
# Token Obtain (login)
# -------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        tokens = response.data
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')

        res = Response({'success': True})
        res.data.update(tokens)

        # Set cookies
        res.set_cookie('access_token', access_token, httponly=True, secure=False, samesite='None', path='/')
        res.set_cookie('refresh_token', refresh_token, httponly=True, secure=False, samesite='None', path='/')
        csrf_token = get_token(request)
        res.set_cookie('csrf_token', csrf_token, httponly=False, secure=False, samesite='None', path='/')
        return res


# -------------------------
# Token Refresh
# -------------------------
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'refreshed': False, 'error': 'No refresh token'})
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        tokens = response.data
        access_token = tokens.get('access')
        res = Response({'refreshed': True})
        if access_token:
            res.set_cookie('access_token', access_token, httponly=True, secure=False, samesite='None', path='/')
        return res


# -------------------------
# Logout (requires JWT cookie)
# -------------------------
@csrf_exempt  # local dev only
@api_view(['POST'])
@authentication_classes([CookiesJWTAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    res = Response({'success': True})
    res.delete_cookie('access_token', path='/', samesite='None')
    res.delete_cookie('refresh_token', path='/', samesite='None')
    res.delete_cookie('csrf_token', path='/', samesite='None')
    return res


# -------------------------
# Check login status
# -------------------------
@api_view(['GET'])
@authentication_classes([CookiesJWTAuthentication])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    serializer = UserSerializer(request.user, many=False)
    return Response(serializer.data)
