"""Firebase token verification without Admin SDK.

Verifies Firebase ID tokens using Google's public certificates.
No service account JSON file needed.
"""

import logging
import time

import requests
import jwt  # PyJWT
from cryptography.x509 import load_pem_x509_certificate

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = "fsassignintern"

# Google's public cert endpoint for Firebase tokens
_GOOGLE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_cached_keys = None
_keys_expiry = 0


def _get_public_keys():
    """Fetch Google's public certs and extract RSA public keys."""
    global _cached_keys, _keys_expiry
    now = time.time()
    if _cached_keys and now < _keys_expiry:
        return _cached_keys

    resp = requests.get(_GOOGLE_CERTS_URL)
    resp.raise_for_status()
    certs = resp.json()

    # Convert X.509 PEM certs to public keys
    keys = {}
    for kid, cert_pem in certs.items():
        cert = load_pem_x509_certificate(cert_pem.encode("utf-8"))
        keys[kid] = cert.public_key()

    _cached_keys = keys

    # Cache based on max-age header
    cache_control = resp.headers.get("Cache-Control", "")
    max_age = 3600
    for part in cache_control.split(","):
        part = part.strip()
        if part.startswith("max-age="):
            try:
                max_age = int(part.split("=")[1])
            except ValueError:
                pass
    _keys_expiry = now + max_age

    return _cached_keys


def verify_firebase_token(id_token):
    """Verify a Firebase ID token using Google's public keys.

    Returns:
        dict with uid, email, and other claims.

    Raises:
        ValueError: If the token is invalid or expired.
    """
    try:
        # Get the kid from the token header
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("Token missing kid header")

        keys = _get_public_keys()
        public_key = keys.get(kid)
        if not public_key:
            # Refresh keys in case they rotated
            global _keys_expiry
            _keys_expiry = 0
            keys = _get_public_keys()
            public_key = keys.get(kid)
            if not public_key:
                raise ValueError("No matching certificate for token")

        # Verify and decode
        decoded = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=FIREBASE_PROJECT_ID,
            issuer=f"https://securetoken.google.com/{FIREBASE_PROJECT_ID}",
        )

        if "sub" not in decoded or not decoded["sub"]:
            raise ValueError("Token missing sub claim")

        decoded["uid"] = decoded["sub"]
        return decoded

    except jwt.ExpiredSignatureError:
        raise ValueError("Firebase token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid Firebase token: {e}")
    except Exception as e:
        raise ValueError(f"Firebase token verification failed: {e}")
