from celery import shared_task
from django.utils import timezone
from .models import Item, Transaction


@shared_task
def open_auction(item_id):
    """
    Sets the status field in item model as active.
    """

    try:
        item = Item.objects.get(id=item_id)
        if item.start_time <= timezone.now() < item.end_time:
            item.status = 'active'
            item.save()

    except Exception as e:
        print(f"Some error occured: {e}")


@shared_task
def close_auction(item_id):
    """
    Set the status field as closed and calculates winner.
    """

    try:
        item = Item.objects.get(id=item_id)
        if item.end_time <= timezone.now():
            item.status = 'closed'
            item.save()
        # Reverse lookup to get all the bids for the given item.
        winning_bid = item.bids.order_by('-bid_amount').first()
        if winning_bid:
            item.winner = winning_bid.user
            item.save()

            Transaction.objects.create(
                buyer=winning_bid.user,
                item=winning_bid.item,
                amount=winning_bid.bid_amount
            )

        return f"Auction for {item.name} closed successfully! Winner: {item.winner.username if item.winner else 'No bids placed'}"
    except Exception as e:
        pass


@shared_task
def test_task():
    print("Test task executed")
    return "Test task executed successfully"
