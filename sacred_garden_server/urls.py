from django.contrib import admin
from django.urls import path, include

from sacred_garden import urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sacred_garden/v1/', include(urls.urlpatterns)),
]
