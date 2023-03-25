from django.urls import path, include


from sacred_garden import views

router = routers.DefaultRouter()
router.register(r'home', views.home)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
