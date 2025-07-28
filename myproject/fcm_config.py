import os

import firebase_admin
from django.conf import settings
from firebase_admin import credentials

cred_path = os.path.join(settings.BASE_DIR, "gardening_secrets.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
