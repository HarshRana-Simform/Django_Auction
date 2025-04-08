from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import open_auction, close_auction
from .models import Item, Bid


@receiver(post_save, sender=Item)
def schedule_auction_tasks(sender, instance, created, **kwargs):
    """Schedule tasks to open and close auction based on start and end times"""

    print("Signal to schedule the tasks called.")

    if created:
        # Scheduling the open task
        delay_open = instance.start_time
        open_auction.apply_async(args=[instance.id], eta=delay_open)

        # Scheduling the close task
        delay_close = instance.end_time
        close_auction.apply_async(args=[instance.id], eta=delay_close)
