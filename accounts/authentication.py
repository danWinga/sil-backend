# # accounts/authentication.py

# import requests
# import jwt
# import time
# from cachetools import TTLCache, cached
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from rest_framework import authentication, exceptions

# User = get_user_model()

# # cache the JWKS for 5 minutes
# _jwks_cache = TTLCache(maxsize=1, ttl=300)

# @cached(_jwks_cache)
# def fetch_jwks():
#     # discover OIDC config
#     cfg = requests.get(f"{settings.OIDC_OP_ISSUER}/.well-known/openid-configuration", timeout=5).json()
#     jwks_uri = cfg["jwks_uri"]
#     return requests.get(jwks_uri, timeout=5).json()["keys"]


# class CustomOIDCBearerAuthentication(authentication.BaseAuthentication):
#     """
# #     Validate OIDC-issued JWTs, map to Customer.
# #     """

#     def authenticate(self, request):
#         auth = authentication.get_authorization_header(request).split()
#         if not auth or auth[0].lower() != b"bearer":
#             return None
#         token = auth[1]
#         try:
#             unverified_header = jwt.get_unverified_header(token)
#             keys = fetch_jwks()
#             jwk = next((k for k in keys if k["kid"] == unverified_header["kid"]), None)
#             if not jwk:
#                 raise exceptions.AuthenticationFailed("JWK not found")
#             public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

#             payload = jwt.decode(
#                 token,
#                 key=public_key,
#                 algorithms=["RS256"],
#                 issuer=settings.OIDC_OP_ISSUER,
#                 options={"require": ["exp", "iss"], "verify_aud": False},
#             )
#             if payload.get("azp") != settings.OIDC_RP_CLIENT_ID:
#                 raise exceptions.AuthenticationFailed("Invalid azp claim")
#         except requests.RequestException as e:
#             raise exceptions.AuthenticationFailed(f"OIDC discovery error: {e}")
#         except jwt.ExpiredSignatureError:
#             raise exceptions.AuthenticationFailed("Token expired")
#         except jwt.InvalidIssuerError:
#             raise exceptions.AuthenticationFailed("Invalid issuer")
#         except jwt.InvalidTokenError as e:
#             raise exceptions.AuthenticationFailed(f"Invalid token: {e}")

#         email = payload.get("email")
#         if not email:
#             raise exceptions.AuthenticationFailed("Token missing email")
#         username = payload.get("preferred_username") or payload.get("sub")
#         user, _ = User.objects.get_or_create(
#             email=email, defaults={"username": username}
#         )
#         return (user, None)


# accounts/authentication.py

import jwt
import requests
from cachetools import TTLCache, cached
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

User = get_user_model()

# cache the JWKS for 5 minutes
_jwks_cache = TTLCache(maxsize=1, ttl=300)


@cached(_jwks_cache)
def fetch_jwks():
    cfg = requests.get(
        f"{settings.OIDC_OP_ISSUER}/.well-known/openid-configuration", timeout=5
    ).json()
    return requests.get(cfg["jwks_uri"], timeout=5).json()["keys"]


class CustomOIDCBearerAuthentication(authentication.BaseAuthentication):
    """
    Validate OIDC-issued JWTs by:
      - verifying signature & expiry
      - fetching JWKS
      - enforcing 'azp' == our client
      - mapping email→Customer
    """

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].lower() != b"bearer":
            return None

        token = auth[1]
        try:
            # 1) find the right JWK
            header = jwt.get_unverified_header(token)
            keys = fetch_jwks()
            jwk = next((k for k in keys if k["kid"] == header.get("kid")), None)
            if not jwk:
                raise exceptions.AuthenticationFailed("JWK not found")

            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

            # 2) decode & verify signature + expiry ONLY
            payload = jwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": False,
                    "verify_aud": False,
                },
            )

            # 3) ensure this token was issued to our client
            if payload.get("azp") != settings.OIDC_RP_CLIENT_ID:
                raise exceptions.AuthenticationFailed("Invalid azp (client) claim")

        except requests.RequestException as e:
            raise exceptions.AuthenticationFailed(f"OIDC discovery error: {e}")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {e}")

        # 4) map to Customer
        email = payload.get("email")
        if not email:
            raise exceptions.AuthenticationFailed("Token missing email claim")
        username = payload.get("preferred_username") or payload.get("sub")
        user, _ = User.objects.get_or_create(
            email=email, defaults={"username": username}
        )
        return (user, None)
