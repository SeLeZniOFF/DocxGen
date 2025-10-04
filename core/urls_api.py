from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EntityViewSet, ClientViewSet,
    TemplateViewSet, GeneratedDocumentViewSet,
    api_generate,
)

router = DefaultRouter()
router.register(r"entities", EntityViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"templates", TemplateViewSet)
router.register(r"generated", GeneratedDocumentViewSet, basename="generated")

urlpatterns = [
    path("", include(router.urls)),
    path("generate/<int:client_id>/<int:template_id>/", api_generate, name="api_generate"),
]