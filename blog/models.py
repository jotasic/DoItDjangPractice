from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.
class Category(models.Model) :
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self) :
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'


    # Admin 페이지에서 보이는 이름 재 정의
    class Meta:
        verbose_name_plural = 'Categories'

class Tag(models.Model) :
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self) :
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'



class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    head_image = models.ImageField(
        upload_to='blog/images/%Y/%m/%d/', blank=True)

    file_upload = models.FileField(
        upload_to='blog/files/%Y/%m/%d/', blank=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, blank=True)

    tags = models.ManyToManyField(Tag, null=True, blank=True)

    def __str__(self):
        return f"[{self.pk}] {self.title} :: {self.author}"
    # author : 추후 작성

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'
