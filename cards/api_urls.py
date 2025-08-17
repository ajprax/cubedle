from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CardViewSet, KernelViewSet, CandidateCardViewSet

router = DefaultRouter()
router.register(r'cards', CardViewSet)
router.register(r'kernels', KernelViewSet)
router.register(r'candidates', CandidateCardViewSet, basename='candidatecard')

urlpatterns = [
    path('', include(router.urls)),
]