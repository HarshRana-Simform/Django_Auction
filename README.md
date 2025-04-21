# Django Auction

A real-time auction platform built with Django and Django Rest Framework (DRF). This application allows users to participate in live auctions, track current and past bids, and manage listings in the backend side along with a simple dashboard interface to monitor auctions.

## Features

- User Dashboard to track active and finished auctions
- Real-time bidding updates
- Admin panel for auction management
- User authentication (login/registration)

## Tech Stack

- **Backend**: Python, Django, Django Rest Framework (DRF)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: Postgresql
- **Real-Time Updates**: Django Channels

## Installation

Follow these steps to set up the project locally:

```bash
# 1. Clone the repository
git clone https://github.com/HarshRana-Simform/Django_Auction.git
cd Django_Auction

# 2. Set up a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create a superuser (for admin access)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver

```

Visit the app at: http://127.0.0.1:8000/
