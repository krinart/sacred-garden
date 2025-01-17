from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework import routers

from sacred_garden import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'sample-data', views.SampleDataViewSet)
router.register(r'emotional-needs', views.EmotionalNeedViewSet)
router.register(r'emotional-need-states', views.EmotionalNeedStateViewSet)
router.register(r'emotional-letters', views.EmotionalLetterViewSet)

urlpatterns = [
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
    path('appreciations/', views.AppreciationsAPIView.as_view(), name='appreciations'),
    path('check-user/', views.CheckUserView.as_view(), name='check-user'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('join-wait-list/', views.JoinWaitListView.as_view(), name='join-wait-list'),
    path('request-reset-password/', views.RequestResetPassword.as_view(), name='request-password-reset'),
    path('reset-password/', views.ResetPassword.as_view(), name='reset-password'),
]


urlpatterns += router.urls
