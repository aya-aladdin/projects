from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new_post, name="new_post"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("follow/<str:username>/", views.follow_user, name="follow_user"),
    path("followed-posts/", views.followed_posts, name="followed_posts"),
    path("all-posts/", views.all_posts, name="all_posts"),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path("post/<int:post_id>/reply/", views.reply_post, name="reply_post"),
]