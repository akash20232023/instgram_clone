from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from . import utilities
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.db.models import Q
timeout = getattr(settings, 'PANEL_SESSION_TIMEOUT', None)


def index(request):
    return render(request, 'index.html')


def login_form(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        admin_userObj, uflag = utilities.check_admin_status(username)
        if uflag:
            user = authenticate(username=admin_userObj.username, password=password)
            if user is not None:
                # request.session.set_expiry(timeout)/
                login(request, user)
                return redirect('home')
            else:
                msg = "Invalid Password"
                return render(request, 'login.html', {'error_message': msg})
        else:
            msg = "User does not exist"
            return render(request, 'login.html', {'error_message': msg})
    else:
        return render(request, 'login.html')
    

@login_required
def logout_view(request):
    logout(request)
    return HttpResponse('/')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        bio = request.POST.get("bio", None)
        avatar = request.FILES.get("avatar")
        gender = request.POST.get("gender", None)
        
        if not (username and password and confirm_password and first_name and last_name):
            msg = "Please fill all required fields."
            return render(request, 'signup.html', {'msg': msg})
        
        if password != confirm_password:
            msg = "Please ensure that the passwords and confirm password match."
            return render(request, 'signup.html', {'msg': msg})
        
        if User.objects.filter(username=username).exists():
            msg = "Username already taken. Please choose another username"
            return render(request, 'signup.html', {'msg': msg})

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
                user.save()

                profile_create = Profile()
                profile_create.user = user
                profile_create.first_name = first_name
                profile_create.last_name = last_name
                profile_create.bio = bio
                profile_create.gender = gender
                profile_create.save()

                if avatar:
                    img_flag, path = utilities.upload_image_base64(avatar)
                    if not img_flag:
                        msg = "Invalid choice of image."
                        return render(request, 'signup.html', {'msg': msg})

                    profile_create.avatar = path
                    profile_create.save()

                msg = "User successfully registered."
                return render(request, 'signup.html', {'success_msg': msg})
        except Exception as e:
            msg = "An error occurred. Please try again."
            return render(request, 'signup.html', {'msg': msg})

    return render(request, 'signup.html')


@login_required
def home_page(request):
    user = request.user.profile
    posts = Follow.objects.filter(profile=user)
    post_list = []
    if posts:
        followed_profile = posts[0].following.all()
        if followed_profile:
            posts = Post.objects.filter(profile__in=followed_profile, soft_delete=False)
            if posts:
                for post in posts:
                    admin = post.admin
                    admin_name = str(admin.first_name + admin.last_name) if admin.first_name and admin.last_name else None
                    post_imgs = list(PostImage.objects.filter(soft_delete=False,post=post).values("id","image"))
                    likes = post.likes.all()
                    likes_list = [
                        {'id': like.id, 
                        'name': str(like.first_name + like.last_name) if like.first_name and like.last_name else None
                        } for like in likes] if likes else []

                    comments = Comment.objects.filter(post=post, soft_delete=False)
                    comment_list = [
                        {
                            'text': comment.text, 
                            'profile': f"{comment.profile.first_name} {comment.profile.last_name}" if comment.profile.first_name and comment.profile.last_name else None, 
                            "user_id" : comment.profile.id
                            } for comment in comments] if comments else []

                    data_dict = {
                        "id" :post.id,
                        "admin" : admin_name,
                        "caption" : post.caption,
                        "post_images" : post_imgs if post_imgs else [],
                        "likes" : likes_list,
                        "comment_list" : comment_list
                    }
                    post_list.append(data_dict)


    user_posts = Post.objects.filter(profile=user, soft_delete=False)
    if user_posts:
        for post in user_posts:
            admin = post.profile
            admin_name = str(admin.first_name + admin.last_name) if admin.first_name and admin.last_name else None
            post_imgs = list(PostImage.objects.filter(soft_delete=False,post=post).values("id","image"))
            likes = post.likes.all()
            likes_list = [
                {'id': like.id, 
                'name': str(like.first_name + like.last_name) if like.first_name and like.last_name else None
                } for like in likes] if likes else []
            
            comments = Comment.objects.filter(post=post, soft_delete=False)
            comment_list = [
                {
                    'text': comment.text, 
                    'profile': f"{comment.profile.first_name} {comment.profile.last_name}" if comment.profile.first_name and comment.profile.last_name else None, 
                    "user_id" : comment.profile.id
                } for comment in comments] if comments else []

            data_dict = {
                "id" :post.id,
                "admin" : admin_name,
                "caption" : post.caption,
                "post_images" : post_imgs if post_imgs else [],
                "likes" : likes_list,
                "comment_list" : comment_list
            }
            post_list.append(data_dict)
    return render(request, 'home.html', {'posts': post_list})


@login_required
def my_profile(request):
    admin = request.user.profile
    first_name = admin.first_name
    last_name = admin.last_name
    bio = admin.bio if admin.bio else None
    gender = admin.gender
    avatar = admin.avatar.url if admin.avatar else None

    context = {
        "id" : admin.id,
        "first_name" : first_name,
        "last_name" : last_name,
        "bio" : bio,
        "gender" : gender,
        "avatar" : avatar
    }

    posts = Post.objects.filter(soft_delete=False, profile=admin)
    post_list = []
    if posts:
        for post in posts:
            admin = post.profile
            admin_name = str(admin.first_name + admin.last_name) if admin.first_name and admin.last_name else None
            post_imgs = list(PostImage.objects.filter(soft_delete=False,post=post).values("id","image"))
            likes = post.likes.all()
            likes_list = [
                {'id': like.id, 
                'name': str(like.first_name + like.last_name) if like.first_name and like.last_name else None
                } for like in likes] if likes else []

            data_dict = {
                "id" :post.id,
                "admin" : admin_name,
                "caption" : post.caption,
                "post_images" : post_imgs if post_imgs else [],
                "likes" : likes_list
            }
            post_list.append(data_dict)

    follow_list = Follow.objects.filter(soft_delete=False,profile=admin)
    following_list = []
    follower_list = []

    if follow_list:
        followers = follow_list[0].follower.all()
        followings = follow_list[0].following.all()
        
        follower_list = [
                {'id': follower.id, 
                'name': str(follower.first_name + follower.last_name) if follower.first_name and follower.last_name else None
                } for follower in followers] if followers else []

        following_list = [
                {'id': following.id, 
                'name': str(following.first_name + following.last_name) if following.first_name and following.last_name else None
                } for following in followings] if followings else []

    context["posts"] = post_list
    context["followers"] = follower_list
    context["followings"] = following_list

    return render(request, 'profile.html', context)


@login_required
def add_post(request):
    msg = ''
    if request.method == 'POST':
        admin = request.user.profile

        caption = request.POST.get("caption")
        post_images = request.FILES.get("post_images", None)

        try:
            with transaction.atomic():
                post = Post()
                post.profile = admin
                post.caption = caption
                post.save()

                if post_images:
                    img_flag, path = utilities.upload_image_base64(post_images)
                    if not img_flag:
                        msg = "Invalid choice of image."
                        return render(request, 'post-add.html', {'msg': msg})
                    post_img = PostImage.objects.create(
                        post=post,
                        image=path
                    )
                    return redirect('home')

        except Exception as e:
            msg = str(e)
    return render(request, 'post-add.html', {'msg': msg})


@login_required
def add_comment(request, post_id=None):
    msg = ''
    admin = request.user.profile
    if not post_id:
        msg = 'Please eneter the post id'
        return render(request, 'home.html',{'msg':msg})
    
    comment_text = request.POST.get("text")
    
    try:
        post = Post.objects.get(soft_delete=False,id=post_id)
        comment = Comment()
        comment.profile = admin
        comment.text = comment_text
        comment.post = post
        comment.save()
    except Exception as e:
        msg = str(e)
    
    return redirect('/home/')


@login_required
def add_like(request, post_id=None):
    msg = ''
    admin = request.user.profile
    if not post_id:
        msg = 'Please eneter the post id'
        return render(request, 'home.html',{'msg':msg})
    try:
        post = Post.objects.get(soft_delete=False,id=post_id)
        post.likes.add(admin)
    except Exception as e:
        msg = str(e)
    
    return redirect('/home/')

            

@login_required
def search_feed(request):
    user_name = request.GET.get("username")
    profiles = Profile.objects.filter(soft_delete=False)
    user_list = [] 
    if user_name:
        payload = (
            Q(user__username__icontains=str(user_name)) |
            Q(first_name__icontains=str(user_name)) | 
            Q(last_name__icontains=str(user_name))
            )
        profiles =profiles.filter(payload)
    
    for profile in profiles:
        data_dict = {
            'id' : profile.id,
            "username" : profile.user.username,
            'full_name' : str(profile.first_name + profile.last_name) if profile.first_name and profile.last_name else None
        }
        user_list.append(data_dict)

    return render(request, 'search_feed.html', {'user_list': user_list})

@login_required
def follow_api(request, user_id=None):
    msg = ''
    user = request.user.profile
    try:
        follow_user = Profile.objects.get(id=user_id)
        follow = Follow()
        follow.profile = user
        follow.save()
        follow.following.add(follow_user)
    except Exception as e:
        msg = str(e)
    
    return redirect('/search_feed/')
    

@login_required
def user_profile(request, user_id=None):
    msg = ''
    try:
        profile = Profile.objects.get(id=user_id)
        context = {
            "id" : profile.id,
            "first_name" : profile.first_name if profile.first_name else None,
            "last_name" : profile.last_name if profile.last_name else None,
            "bio" : profile.bio if profile.bio else None,
            "gender" : profile.gender if profile.gender else None,
            "avatar" : profile.avatar.url if profile.avatar else None
        }
        posts = Post.objects.filter(soft_delete=False, profile=profile)

        post_list = []
        if posts:
            for post in posts:
                admin = post.profile
                admin_name = str(admin.first_name + admin.last_name) if admin.first_name and admin.last_name else None
                post_imgs = list(PostImage.objects.filter(soft_delete=False,post=post).values("id","image"))
                likes = post.likes.all()
                likes_list = [
                    {'id': like.id, 
                    'name': str(like.first_name + like.last_name) if like.first_name and like.last_name else None
                    } for like in likes] if likes else []

                data_dict = {
                    "id" :post.id,
                    "admin" : admin_name,
                    "caption" : post.caption,
                    "post_images" : post_imgs if post_imgs else [],
                    "likes" : likes_list
                }
                post_list.append(data_dict)

        follow_list = Follow.objects.filter(soft_delete=False,profile=profile)
        following_list = []
        follower_list = []

        if follow_list:
            followers = follow_list[0].follower.all()
            followings = follow_list[0].following.all()
            
            follower_list = [
                    {'id': follower.id, 
                    'name': str(follower.first_name + follower.last_name) if follower.first_name and follower.last_name else None
                    } for follower in followers] if followers else []

            following_list = [
                    {'id': following.id, 
                    'name': str(following.first_name + following.last_name) if following.first_name and following.last_name else None
                    } for following in followings] if followings else []

        context["posts"] = post_list
        context["followers"] = follower_list
        context["followings"] = following_list

        return render(request, 'profile.html', context)

    except Exception as e:
        msg = str(e)

    return render
