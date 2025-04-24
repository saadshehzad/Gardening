from django.contrib import admin

from .models import *

admin.site.register(UserPost)
admin.site.register(Articles)
admin.site.register(ReportProblem)
admin.site.register(UserPostLike)
admin.site.register(UserPostShare)
admin.site.register(UserPostComment)
admin.site.register(Post)
