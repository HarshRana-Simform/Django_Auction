from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.


class User(AbstractUser):

    USER_TYPE = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=USER_TYPE, default='buyer')

    groups = models.ManyToManyField(
        Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions", blank=True)

    def __str__(self):
        return self.username


class Item(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=250)
    description = models.TextField()
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='closed')
    winner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_items')

    def __str__(self):
        return self.name


class Bid(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_bid')
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} bid {self.bid_amount} on {self.item.name} at {self.timestamp}.'


class Transaction(models.Model):

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction_id : {self.id}, Item:{self.item.name}, Sold_To:{self.buyer.username}, Amount:{self.amount}'
