import requests
import asyncio
from getpass import getpass
from django.utils import timezone
from datetime import timedelta, datetime


def callAPI(p_url, method='GET', *args, **kwargs):
    method_map = {
        'GET': requests.get,
        'POST': requests.post,
        'PUT': requests.put,
        'DELETE': requests.delete,
        'PATCH': requests.patch
    }

    req_method = method_map[method]

    get_response = req_method(p_url, *args, **kwargs)

    print(get_response.json())

    return get_response


def getAuthenticate():

    # p_username = str(input('Enter username: '))
    # p_password = str(input('Enter password: '))
    password = getpass()

    l_body = {
        'username': 'testuser',
        'password': password
    }

    auth_response = callAPI(
        'http://127.0.0.1:8000/core/api/token/', 'POST', json=l_body)
    return auth_response

# def view_teachers_list():


def main():
    auth_response = getAuthenticate()

    if auth_response.status_code == 200:
        access = auth_response.json()['access']
        headers = {
            'Authorization': f'Bearer {access}'
        }

        callAPI('http://127.0.0.1:8000/core/api/create_item/', headers=headers, method='POST', json={
            "name": "Watch two",
            "description": "Test kar raha.",
            "image": None,
            "starting_bid": 500.00,
            "start_time": (datetime.now() + timedelta(seconds=10)).isoformat(),
            "end_time": (datetime.now() + timedelta(seconds=50)).isoformat()
        })
    else:
        print(auth_response)


main()

# asyncio.run(main())
