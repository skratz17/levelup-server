"""Route configuration"""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from levelupapi.views import register_user, login_user
from levelupapi.views import GameTypes, Games, Events, Profile

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'gametypes', GameTypes, 'gametype')
router.register(r'games', Games, 'game')
router.register(r'events', Events, 'event')
router.register(r'profile', Profile, 'profile')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('levelupreports.urls')),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
] 
