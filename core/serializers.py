from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Item

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
