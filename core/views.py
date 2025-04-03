from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserRegistrationSerializer, ItemSerializer
from django.contrib.auth import get_user_model
from rest_framework import generics, mixins
from .permissions import IsAdmin, IsBuyer, IsSeller
from .models import Item
# Create your views here.

User = get_user_model()


class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response('Hello world')


# class UserRegistrationView(APIView):

#     def post(self, request, format=None):
#         serializer = UserRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message": "User registrered successfully!"},
#                 status=status.HTTP_201_CREATED
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProtectedView(APIView):
    permission_classes = [IsSeller]

    def get(self, request):
        return Response({"message": f"{request.user} have access as your role is {request.user.role}"})


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"User": f"{request.user}",
                        "Role": f"{request.user.role}"})


class LogoutView(APIView):
    """
    This function takes the refresh token in the body and blacklists it to
    logout a user.
    The access token must also be passed in the authorization header.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Getting the refresh token from the request body.
            refresh_token = request.data["refresh"]
            print(refresh_token)
            # Converting it into a token ojject so that it can be manipulatied by simplejwt package.
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": f"Invalid Token: {e}"}, status=status.HTTP_400_BAD_REQUEST)


class CreateItemView(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsSeller]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
