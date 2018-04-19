import django
import json
import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bibstat.settings")

from django.conf import settings
from mongoengine.django.auth import User

user = User.create_user(email = '',
                        username = '',
                        password = '')


user.is_active = True
user.is_staff = True
user.is_superuser = True

user.save()

print(user)
