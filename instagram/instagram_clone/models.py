from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    MALE = "male"
    FEMALE = "female"
    OTHERS = "others"

    GENDER_CHOICES = [
        (MALE, 'male'),
        (FEMALE, 'female'),
        (OTHERS, 'others')
    ]
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    soft_delete = models.BooleanField(default=False, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    first_name = models.CharField(default=None, max_length=255, null=True)
    last_name = models.CharField(default=None, max_length=255, null=True)
    bio = models.TextField(default=None, null=True, max_length=255)
    avatar = models.ImageField(upload_to='media/avatar', blank=True, default=None, null=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, null=True, blank=True, default=OTHERS)

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    soft_delete = models.BooleanField(default=False, db_index=True)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    follower = models.ManyToManyField(Profile, related_name='following_profiles')
    following = models.ManyToManyField(Profile, related_name='follower_profiles')


class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    soft_delete = models.BooleanField(default=False, db_index=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    caption = models.TextField(blank=True, default=None, null=True)
    likes = models.ManyToManyField(Profile, blank=True, default=None, related_name='liked_posts')


class PostImage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    soft_delete = models.BooleanField(default=False, db_index=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/posts/', blank=True, default=None, null=True)


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    soft_delete = models.BooleanField(default=False, db_index=True)
    profile = models.ForeignKey(Profile, default=None, null=True, blank=True, on_delete=models.CASCADE,
                                related_name='commented_profiles')
    post = models.ForeignKey(Post, default=None, null=True, blank=True, on_delete=models.CASCADE,
                             related_name='comments')
    text = models.TextField(default=None, null=True, blank=True)
