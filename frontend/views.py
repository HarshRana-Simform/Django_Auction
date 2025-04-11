from django.shortcuts import render
import requests
import json
# Create your views here.


def auction_dashboard(request):
    response = requests.get('http://127.0.0.1:8000/core/api/list_items/')
    auctions = json.loads(response.text)
    context = {'auctions': auctions}
    return render(request, 'frontend/list_auctions.html', context)
