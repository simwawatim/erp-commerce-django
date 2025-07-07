# urls.py
from django.urls import path
from ai.views import FeedView, PredictView

urlpatterns = [
    path('api/feed/', FeedView.as_view(), name='feed'),
    path('api/predict/', PredictView.as_view(), name='predict'),
]
