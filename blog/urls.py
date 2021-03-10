from django.urls import path
from . import views


urlpatterns = [
    # CBV 방식으로 구현
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
    # FBV 방식으로 구현
    # path('', views.index),
    #path('<int:pk>/', views.single_post_page),
]
