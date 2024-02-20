from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('question/<int:question_id>/', views.question_view, name='question_view'),
    path('panel/admin/', views.index_admin, name='index_admin'),
    # path('panel/admin/questions/<int:question_id>/', views.questions_admin, name='questions_admin'),
    path('panel/leaderboard/', views.leaderboard_admin, name='leaderboard_admin'),
    path('', views.index, name='home'),
    
    # other URLs
]


from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)