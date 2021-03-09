from django.db import models

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.pk}] {self.title}"
    # author : 추후 작성
