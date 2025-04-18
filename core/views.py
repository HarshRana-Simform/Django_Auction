from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserRegistrationSerializer, ItemSerializer, BidSerializer, ListItemSerializer
from django.contrib.auth import get_user_model
from rest_framework import generics, mixins
from .permissions import IsAdmin, IsBuyer, IsSeller
from .models import Item, Bid
from rest_framework.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import timedelta
from rest_framework.throttling import UserRateThrottle
from rest_framework import filters
# Create your views here.

User = get_user_model()


class HomeView(APIView):
    """
    View for the home page.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response('Hello world')


class UserRegistrationView(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    View to register a user in the database.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProtectedView(APIView):
    """
    A view to test with different stuff/ Testing for learning purposes.
    """
    # permission_classes = [IsSeller]

    def get(self, request):
        # item = Item.objects.get(id=21)
        # winning_bid = item.bids.order_by('-bid_amount').first()
        # print(winning_bid)
        # current_time = timezone.now()
        # upcoming_auctions = Item.objects.filter(start_time__gte=current_time)
        # print(upcoming_auctions)
        # print(self.request.user)
        # print(request.headers)
        # user = User.objects.get(id=6)

        # user_bid = user.user_bid.all()

        # print(list(user_bid))
        print(type(self.request.user))
        # print((item.end_time - item.start_time) - timedelta(minutes=3))
        return Response({"message": "Hello"})


class UserDetailsView(APIView):
    """
    View to show the name and role of the user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(self.request.user)
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


class CreateItemView(mixins.CreateModelMixin,
                     generics.GenericAPIView):
    """
    Creates item view with a throttle limit for 2 requests per minute.

    Only users with role seller are allowed.
    """
    throttle_scope = 'item'
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsSeller]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListItemView(mixins.ListModelMixin,
                   generics.GenericAPIView):
    """
    A public api view which lists all the items.
    Called in the frontend app for data presentation.
    """
    queryset = Item.objects.all()
    serializer_class = ListItemSerializer
    # permission_classes = [IsSeller | IsBuyer]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['status', 'id']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UpdateItemView(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     generics.GenericAPIView):
    """
    Updates items with a throttle limit for 2 requests per minute.

    Only users with role seller are allowed.
    """
    throttle_scope = 'item'
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsSeller]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.seller != self.request.user:
            raise PermissionDenied(
                "You are not owner of this item listing.")
        serializer.save()


class DeleteItemView(generics.RetrieveDestroyAPIView):
    """
    Delete items selected.
    Admins can delete all items.
    Users with role seller are allowed to delete thir own item.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsSeller | IsAdmin]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if (instance.seller == self.request.user) or self.request.user.role == 'admin':
            try:
                print(self.request.user.role)
                instance.delete()
            except Exception as e:
                return Response({"error": f"Some error occured: {e}"})

        else:
            raise PermissionDenied(
                "You are not owner of this item listing or don't have sufficient permissions.")


class CreateBidView(mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    """
    Creates bid for the given item in the specified time.

    Only users with role buyer can access.
    """
    throttle_scope = 'bids'
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsBuyer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListBidHistoryView(mixins.ListModelMixin,
                         generics.GenericAPIView):
    """
    Lists the bid history for a selected item.
    """

    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        item_id = self.kwargs.get("item_id")
        return Bid.objects.filter(item_id=item_id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class SendEmailView(APIView):
    """
    A test api to see if the mail system works.
    """

    def post(self, request):
        email = request.data['to']

        emailm = EmailMessage(
            'Testing mail',
            'This is the body of the mail',
            settings.EMAIL_HOST_USER,
            [email]
        )
        emailm.send(fail_silently=False)
        return Response({"message": "Email sent successfully!!"}, status=status.HTTP_200_OK)
