"""Route configuration"""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from levelupapi.views import register_user, login_user, GameTypes

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'gametypes', GameTypes, 'gametype')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
]
