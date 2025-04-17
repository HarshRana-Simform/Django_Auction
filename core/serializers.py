from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Item, Bid
from django.utils import timezone

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'role']

    def validate(self, data):
        """Ensure passwords match before saving."""
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create a new user with a hashed password."""
        validated_data.pop("password2")  # Remove password2 before saving
        # Uses Django's built-in create_user
        user = User.objects.create_user(**validated_data)
        return user


class ItemSerializer(serializers.ModelSerializer):

    seller = serializers.StringRelatedField()

    class Meta:
        model = Item
        fields = ["name", "description", "image", "starting_bid",
                  "current_bid", "start_time", "end_time", "seller"]
        # As it will be filled directly depending on the user.
        read_only_fields = ["seller"]

    def validate_starting_bid(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "The starting bid must be greater than 0.")
        return value

    def validate_start_time(self, value):

        if value <= timezone.now():
            raise serializers.ValidationError(
                "The start time cannot be in the past.")
        return value

    def validate(self, data):

        if data["end_time"] <= data["start_time"]:
            raise serializers.ValidationError(
                "The end time cannot be before the start time.")
        return data


class ListItemSerializer(serializers.ModelSerializer):

    seller = serializers.StringRelatedField()
    winner = serializers.StringRelatedField()
    start_time = serializers.DateTimeField(format="%B %d, %Y %I:%M %p")
    end_time = serializers.DateTimeField(format="%B %d, %Y %I:%M %p")

    class Meta:
        model = Item
        fields = ["id", "name", "description", "image", "starting_bid",
                  "current_bid", "start_time", "end_time", "seller", "status", "winner"]
        # As it will be filled directly depending on the user.
        read_only_fields = ["seller", "winner"]


class BidSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField()

    class Meta:
        model = Bid
        fields = ["user", "item", "bid_amount", "timestamp"]
        read_only_fields = ["user", "timestamp"]

    def validate(self, data):
        item = data["item"]

        if item.end_time < timezone.now():
            raise serializers.ValidationError(
                "The auction has already ended.")
        if timezone.now() < item.start_time:
            raise serializers.ValidationError(
                f"The auction has not started yet: Start date and time:{item.start_time}.")
        if data["bid_amount"] <= item.current_bid:
            raise serializers.ValidationError(
                "Your bid amount must be greater than the current bid.")
        if item.status == 'active':
            return data
        else:
            raise serializers.ValidationError(
                "The auction status is closed, bids are only allowed if the status is active."
            )
