# registrations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationViewSet
from django.urls import path
from . import views
router = DefaultRouter()
router.register(r'apply', RegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
    # 增量添加报名和准考证模块 API
    path('api/registrations/', include('registrations.urls')),

]