from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/',views.login_form, name='login'),
    path('logout/',views.logout, name='logout'),
    path('home/',views.home_page,name='home'),
    path('my_profile/',views.my_profile, name='my_profile'),
    path('add_post/',views.add_post, name='add_post'),
    path('add_comment/<int:post_id>/',views.add_comment, name='add_comment'),
    path('add_like/<int:post_id>/',views.add_like, name='add_like'),
    path('follow_api/<int:user_id>/',views.follow_api,name='follow_api'),
    path('search_feed/',views.search_feed, name='search_feed'),
    path('user_profile/<int:user_id>/',views.user_profile, name='user_profile'),
]





