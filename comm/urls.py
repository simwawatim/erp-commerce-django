from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from comm import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("api.urls")),
    path('ai/', include("ai.urls"))
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


