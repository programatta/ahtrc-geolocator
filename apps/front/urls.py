from django.urls import path
from apps.front.views import HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='homepage')
]
