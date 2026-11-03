from rest_framework.permissions import BasePermission


class IsStudioAdmin(BasePermission):
    """
    Grants access only to authenticated Django staff users.
    """

    message = "You do not have permission to manage studio bookings."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
