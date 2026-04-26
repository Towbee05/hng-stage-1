from django.urls import path, include
# from .views import CoreViewSet
from .views import api
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register('', CoreViewSet)

urlpatterns = [
    # path('', include(router.urls))
    path('', api.urls)
]
