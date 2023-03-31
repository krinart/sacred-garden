from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework import routers

from sacred_garden import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
]


urlpatterns += router.urls
