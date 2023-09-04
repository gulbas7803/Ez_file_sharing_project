from django.shortcuts import render
import os
from .models import UploadedFile,UserProfile
from .serializers import UploadedFileSerializer
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.http import FileResponse
from django.shortcuts import get_object_or_404


@api_view(['POST'])
def signup(request, data):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    auth_user = authenticate(username=username, password=password)
    if auth_user is not None:
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Authenticate Failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def validate_token(token):
    pass


@api_view(['POST'])
def email_verify(request):
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    user = validate_token(token)

    if user:
        user.email_verified = True
        user.save()
        return Response({'message': 'Email verification successful.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        auth_login(request, user)
        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def download_file(request, pk=id):
    obj = get_object_or_404(UploadedFile, pk=pk)
    if not obj.file_field:
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
    # Construct the file path
    file_path = os.path.join(settings.MEDIA_ROOT, str(obj.file_field))

    # Check if the file exists
    if not os.path.exists(file_path):
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

    with open(file_path, 'rb') as file:
        response = FileResponse(file)
    return response


@api_view(['GET'])
def list_uploaded_files(request):
    objects_with_files = UploadedFile.objects.filter(file_field__isnull=False)
    serializer = UploadedFileSerializer(objects_with_files, many=True)
    return Response(serializer.data)


class UploadFileView(generics.CreateAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]


def perform_create(self, serializer):
    serializer.save()



