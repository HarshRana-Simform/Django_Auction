from rest_framework import permissions


class IsBuyer(permissions.BasePermission):
    """
    Allows access only to users with the 'buyer' role.
    """

    def has_permission(self, request, view):
        return request.user.role == "buyer"


class IsSeller(permissions.BasePermission):
    """
    Allows access only to users with the 'seller' role.
    """

    def has_permission(self, request, view):
        return request.user.role == "seller"


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with the 'admin' role.
    """

    def has_permission(self, request, view):
        return request.user.role == "admin"
