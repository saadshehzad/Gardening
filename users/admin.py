from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(Region)
admin.site.register(UserRegion)
admin.site.register(UserProfile)
admin.site.register(UserFCMToken)