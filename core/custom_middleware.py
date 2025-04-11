from django.http import JsonResponse
from rest_framework import status


class MaintenanceModeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith('/core/api/'):

            if hasattr(request, 'user') and request.user.is_staff:

                response = self.get_response(request)
                return response
            # Toggling this flag for maintenance enabling.
            maintenance = False

            if maintenance:
                return JsonResponse({"message": "The site is under maintenance."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        response = self.get_response(request)

        return response
