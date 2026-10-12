from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),

    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/history/', views.history_api, name='history_api'),
    path('api/history/clear/', views.clear_history_api, name='clear_history_api'),
    path('api/health/', views.health_check_api, name='health_check_api'),
]
