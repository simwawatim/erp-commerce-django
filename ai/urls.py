# urls.py
from django.urls import path
from ai.views import PredictView

urlpatterns = [
    path('api/predict/', PredictView.as_view(), name='predict'),
]
