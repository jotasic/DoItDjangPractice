from django.contrib import admin
from .models import Post

# Register your models here.

# Admin page의 Post 등록
admin.site.register(Post)
