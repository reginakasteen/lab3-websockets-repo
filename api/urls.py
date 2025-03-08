from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from drf_spectacular.views import SpectacularRedocView, SpectacularAPIView
from django.conf import settings
from django.conf.urls.static import static

from api import views



urlpatterns = [
    path("token/", views.TokenView.as_view(), name="token-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path('set-online/', views.set_online, name='set-online'),
    path('set-offline/', views.set_offline, name='set-offline'),


    path("todo/<user_id>/", views.TodoListView.as_view(), name="todo"),
    path("todo-detail/<user_id>/<task_id>/", views.TodoDetailView.as_view(), name="todo-detail"),
    path("todo-completed/<user_id>/<task_id>/", views.TodoCompletedView.as_view(), name="todo-completed"),

    path("my-messages/<user_id>/", views.Inbox.as_view(), name="inbox"),
    path("get-messages/<sender_id>/<receiver_id>/", views.GetMessagesView.as_view(), name="messages"),
    path("send-message/", views.SendMessage.as_view(), name="send"),
    path("profile/<int:pk>/", views.ProfileDetailView.as_view(), name="profile"),
    path('profile/<int:user_id>/', views.ProfileView.as_view(), name='profile-detail'),
    path("search/<username>/", views.UserSearch.as_view(), name="search"),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

