from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import User, Post, Follow, Like, Reply

def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/index.html', {
        'posts': page_obj
    })

@csrf_exempt
@login_required
def new_post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")
        if content:
            post = Post(author=request.user, content=content)
            post.save()
            return JsonResponse({
                "message": "Post created successfully!",
                "post": {
                    "author": post.author.username,
                    "content": post.content,
                    "likes": post.likes.count(),
                    "id": post.id
                }
            }, status=201)
        return JsonResponse({"error": "Content cannot be empty!"}, status=400)
    return JsonResponse({"error": "Invalid request method!"}, status=405)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})
    return JsonResponse({"error": "Invalid request method!"}, status=405)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def reply_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        reply_content = request.POST.get('reply-content')
        Reply.objects.create(post=post, author=request.user, content=reply_content)
        return redirect('post_detail', post_id=post.id)  # Redirect to the post detail page

    return redirect('post_detail', post_id=post.id)  # Redirect to the post detail page if not POST

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).order_by('-timestamp')
    followers = Follow.objects.filter(followed_user=profile_user)
    following = Follow.objects.filter(follower=profile_user)
    
    followers_count = followers.count()
    following_count = following.count()

    recent_follower = followers.order_by('-id').first()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, followed_user=profile_user).exists()

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'follower': recent_follower.follower if recent_follower else None,
        'is_following': is_following,
    }
    return render(request, 'network/profile.html', context)

@login_required
def follow_user(request, username):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    profile_user = get_object_or_404(User, username=username)
    is_following = Follow.objects.filter(follower=request.user, followed_user=profile_user).exists()
    if is_following:
        Follow.objects.filter(follower=request.user, followed_user=profile_user).delete()
        is_following = False
    else:
        Follow.objects.create(follower=request.user, followed_user=profile_user)
        is_following = True
    followers_count = Follow.objects.filter(followed_user=profile_user).count()
    return JsonResponse({'success': True, 'is_following': is_following, 'followers_count': followers_count})


@login_required
def followed_posts(request):
    followed_users = Follow.objects.filter(follower=request.user).values_list('followed_user', flat=True)
    posts = Post.objects.filter(author__in=followed_users).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/followed_posts.html', {
        'posts': page_obj
    })

@csrf_exempt
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.user:
        return JsonResponse({"success": False, "error": "You do not have permission to edit this post."}, status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        new_content = data.get("content")
        if new_content:
            post.content = new_content
            post.save()
            return JsonResponse({"success": True, "content": post.content})
        return JsonResponse({"success": False, "error": "Content cannot be empty!"}, status=400)
    
    return JsonResponse({"success": False, "error": "Invalid request method!"}, status=405)

def all_posts(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/all_posts.html', {
        'posts': page_obj
    })

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    replies = post.replies.all().order_by('-timestamp')
    return render(request, 'network/post_detail.html', {
        'post': post,
        'replies': replies
    })