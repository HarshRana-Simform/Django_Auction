from celery import shared_task
from django.utils import timezone
from .models import Item, Transaction, User
from django.core.mail import EmailMessage
from django.conf import settings


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
        print(f"Some error occured: {e}")


@shared_task
def send_start_mail(item_id):
    """
    Sends a reminder mail 5 minutes before the starting of the auction.
    """

    try:
        print("Sending a reminder email before the start of the auction.")

        item = Item.objects.get(id=item_id)
        user_emails = User.objects.filter(
            role='buyer').values_list('email', flat=True)

        print(user_emails)

        emailm = EmailMessage(
            f'Reminder: Acution for {item.name}',
            f'This is a reminder email to inform you that the auction for the item {item.name} is going to start at {item.start_time.isoformat()}. Get ready to bid !!!',
            settings.EMAIL_HOST_USER,
            user_emails
        )
        emailm.send(fail_silently=False)
        return "Emails sent successfully!!"

    except Exception as e:
        print(f"Some error occured: {e}")


@shared_task
def send_end_mail(item_id):
    """
    Sends a mail to announce the closing of the auction.
    """

    try:
        print("Sending a mail to announce the closing of the auction.")

        item = Item.objects.get(id=item_id)
        user_emails = User.objects.filter(
            role='buyer').values_list('email', flat=True)

        print(user_emails)

        emailm = EmailMessage(
            f'Closing: Acution for {item.name}',
            f'The auction for the item {item.name} has ended. Winner: {item.winner.username if item.winner else "No bids placed"}. Thank you for participating in it.',
            settings.EMAIL_HOST_USER,
            user_emails
        )
        emailm.send(fail_silently=False)
        return "Emails sent successfully!!"

    except Exception as e:
        print(f"Some error occured: {e}")


@shared_task
def send_upcoming_auctions_emails():

    try:
        current_time = timezone.now()
        upcoming_auctions = Item.objects.filter(start_time__gte=current_time)
        user_emails = User.objects.filter(
            role='buyer').values_list('email', flat=True)

        if upcoming_auctions.exists():
            print("This works!!")
            auctions_list = "\n".join(
                [f"Item:{auction.name}, Start date-time : {auction.start_time}" for auction in upcoming_auctions])

            emailm = EmailMessage(
                f'Upcoming Auctions in the Future',
                f'Here are the auctions starting in the near future:\n\n{auctions_list}',
                settings.EMAIL_HOST_USER,
                user_emails
            )
            emailm.send(fail_silently=False)
            return "Emails sent successfully!!"

    except Exception as e:
        print(f"Some error occured: {e}")
