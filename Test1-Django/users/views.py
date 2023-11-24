from __future__ import annotations
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.response import Response

from .serializers import LoginSerializer
from .serializers import RegisterSerializer
from core_viewsets.custom_viewsets import CreateViewSet
from core_viewsets.custom_viewsets import ListViewSet

# Create your views here.


class RegisterViewSet(CreateViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):

        email = request.data.get('email')
        password = request.data.get('password', None)
        phone_number = request.data.get('phone_number')

        # TODO: Validations

        user = get_user_model().objects.create_user(request.data)

        return Response(
            {'code': 200, 'message': 'success', 'user_id': user._get_pk_val()},
        )


class LoginViewSet(CreateViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = LoginSerializer  # Assuming LoginSerializer is correctly defined

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            # Use Django's built-in authenticate function to check credentials
            user = authenticate(email=email, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Update last login time
                user.last_login = timezone.now()
                user.save()

                return Response({
                    'code': 200,
                    'message': 'success',
                    'access_token': access_token,
                    'user_id': user.pk,
                    'name': user.first_name,
                    'email': user.email,
                    'last_login': user.last_login,
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'code': 401, 'message': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'code': 400, 'message': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import UserSerializer  # Import your UserSerializer here
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from .models import *

class MeViewSet(ListViewSet):
    authentication_classes = (BasicAuthentication,)  # Specify your authentication class
    permission_classes = (IsAuthenticated,)  # Ensure the user is authenticated
    serializer_class = UserSerializer  # Specify your UserSerializer class
    queryset = get_user_model().objects.all()

    def get_object(self):
        return self.request.user  # Get the currently authenticated user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serialized_user = self.get_serializer(instance)  # Serialize the user data

        return Response(serialized_user.data, status=status.HTTP_200_OK)


# views.py
from django.views import View
from django.shortcuts import redirect
import json

import sqlite3

class ProcessDataView(ListViewSet):
    def get(self, request):
        # Read JSON file
        with open('dataset_world_population_by_country_name.json', 'r') as file:
            data = json.load(file)

        # Process and insert data into Django model
        for entry in data:
            country = entry['country']
            population = (
                entry['pop1980'] + entry['pop2000'] + entry['pop2010'] +
                entry['pop2022'] + entry['pop2023'] + entry['pop2030'] + entry['pop2050']
            )
            population.objects.update_or_create(country=country, defaults={'population': population})

        return redirect('http://127.0.0.1:8000/')  # Replace 'your_redirect_url' with the desired redirect URL



import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('tkagg')
import sqlite3
from django.shortcuts import redirect
from django.views import View

class GenerateBarGraphView(ListViewSet):
    def generate_bar_graph_and_save_image(self, request):
        # Retrieve data from SQLite database
        conn = sqlite3.connect('video_db.db')
        df = pd.read_sql_query("SELECT * FROM population", conn)
        conn.close()

        # Create a bar graph
        plt.figure(figsize=(12, 6))
        plt.bar(df['country'], df['population'])
        plt.xlabel('Country')
        plt.ylabel('Population')
        plt.title('Population by Country')
        plt.xticks(rotation=90)
        plt.tight_layout()

        # Save the plot as an image
        plt.savefig('population_bar_chart.png')  # Save as PNG image file

        # Close the plot to avoid displaying it in the response
        plt.close()

        # return redirect('^$')  # Replace 'your_redirect_url' with the desired redirect URL

    def get(self, request):
        return self.generate_bar_graph_and_save_image(request)


# class MeViewSet(ListViewSet):
#     authentication_classes = ()  # ToDO Specify Auth class
#     permission_classes = ()
#     serializer_class = None  # ToDO Specify serializer_class class
#     queryset = get_user_model().objects.all()

#     def list(self, request, *args, **kwargs):
#         # ToDO:  Add your code
#         return Response({})
