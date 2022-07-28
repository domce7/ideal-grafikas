from django.urls import path
from excel_to_ics import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.upload, name='upload'),
    path('upload_list/', views.upload_list, name='upload_list'),
    path('after-upload/', views.after_upload, name='after_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)