from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import open_auction, close_auction, send_start_mail, send_end_mail
from .models import Item, Bid
from datetime import timedelta, datetime
from django.db import connection
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=Item)
def schedule_auction_tasks(sender, instance, created, **kwargs):
    """Schedule tasks to open and close auction based on start and end times"""

    if created:
        print("Signal to schedule the tasks called and set current_bid to starting bid.")

        instance.current_bid = instance.starting_bid
        instance.save()

        # Broadcast to WebSocket clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'auction_dashboard',
            {
                'type': 'send_status_update',
                'item_id': instance.id,
                'status': str(instance.status),
            }
        )

        # Scheduling the open task
        delay_open = instance.start_time
        open_auction.apply_async(
            args=[instance.id], eta=delay_open)

        # Scheduling the close task
        delay_close = instance.end_time
        close_auction.apply_async(args=[instance.id], eta=delay_close)

        delay_start_mail = instance.start_time - timedelta(minutes=5)
        send_start_mail.apply_async(
            args=[instance.id], eta=delay_start_mail)

        delay_end_mail = instance.end_time + timedelta(minutes=1)
        send_end_mail.apply_async(
            args=[instance.id], eta=delay_end_mail)


@receiver(post_save, sender=Bid)
def update_current_bid(sender, instance, created, **kwargs):
    """
    To change the current bid whenever a valid bid is placed.
    """

    if created:

        item = instance.item
        # item.current_bid = instance.bid_amount
        # item.save()

        with connection.cursor() as cursor:
            print("The stored procedure called.")
            cursor.execute(
                "CALL update_current_bid_procedure(%s)", [instance.id])

        # Broadcast to WebSocket clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'auction_dashboard',
            {
                'type': 'send_auction_update',
                'item_id': item.id,
                'current_bid': str(instance.bid_amount),
            }
        )
