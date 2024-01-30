from django.shortcuts import render
from .serializers import MyUserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
import traceback
from .models import MyUser
from django.contrib.auth import authenticate, login
import logging
from .authentication import EmailAuthBackend


class InputException(Exception):
    def __init__(self, *args, **kwargs):
        default_message = "Raising Custom Exception NoOPError: There are no results found for the specified parameters!"
        if not (args or kwargs):
            args = (default_message,)
        super().__init__(*args, **kwargs)

@api_view(["POST", "GET"])
def register(request):
    if request.method == "POST":
        try:
            data = request.data
            data['phone'] = "+91" + data["phone"]
            serializer = MyUserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.error_messages)
            return Response({"status":"success"},status=status.HTTP_200_OK)
        except InputException as e:
            return Response(traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(traceback.format_exc(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(["POST"])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        response = JsonResponse({
            "message": "Login Successfully",
            "code": "HTTP_200_OK",
            "Authorization": token.key,
            "status":"success",
            "user": username
        })
        response.set_cookie("Token", token.key)
        return response
    else:
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

    
@api_view(["POST"])
def reset_password(request):
    if request.method == "POST":
        try:
            data = request.data
            userdata = MyUser.objects.get(email=data["email"])
            serializer = MyUserSerializer(userdata, data=data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(traceback.format_exc(),status=status.HTTP_400_BAD_REQUEST)
