from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetReportViewSet, NotificationViewSet
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'reports', PetReportViewSet, basename='reports')
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    # ===== HOME =====
    path('', views.home_view, name='home'),

    # ===== API ROUTES (DRF) =====
    # We use a sub-prefix for router URLs to avoid hijacking the home page root
    path('api-v1/', include(router.urls)),

    # ===== AUTH =====
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ===== DASHBOARD =====
    path('dashboard/', views.dashboard, name='dashboard'),

    # ===== PET REPORTS =====
    path('add-report/', views.add_report_page, name='add_report'),
    path('edit-report/<int:pk>/', views.edit_report, name='edit_report'),
    path('delete-report/<int:pk>/', views.delete_report, name='delete_report'),

    # ===== SEARCH =====
    path('search/', views.search_pets, name='search_pets'),

    # ===== NOTIFICATIONS =====
    path('notifications-page/', views.notifications_page, name='notifications_page'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),

    # ===== AJAX API (Navbar Polling) =====
    path('api/notifications/unread-count/', views.unread_count_api, name='unread_count_api'),
]