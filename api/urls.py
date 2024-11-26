from django.urls import path
from api.views import api
from django.urls import path

urlpatterns = [
    path("", api.urls),
]