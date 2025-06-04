# config/exceptions.py
# for exception
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Use DRF's default handler, then map authentication errors to 403.
    """
    response = exception_handler(exc, context)

    if response is not None and isinstance(
        exc, (NotAuthenticated, AuthenticationFailed)
    ):
        response.status_code = 403

    return response
