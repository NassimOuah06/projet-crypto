from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer  # Assure-toi que ce serializer existe
from django.contrib.auth.models import User  # Si tu as un modèle User personnalisé, importe-le

@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        # Générer ou récupérer le token de l'utilisateur
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": UserSerializer(user).data  # Renvoie les infos de l'utilisateur
        }, status=status.HTTP_200_OK)
    
    return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    request.user.auth_token.delete()  # Supprime le token
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
