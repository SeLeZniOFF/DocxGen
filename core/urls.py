from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # Entities
    path("entities/", views.entity_list, name="entities_list"),
    path("entities/create/", views.entity_create, name="entity_create"),
    path("entities/<int:pk>/edit/", views.entity_edit, name="entity_edit"),
    path("entities/<int:pk>/delete/", views.entity_delete, name="entity_delete"),

    # Clients
    path("clients/", views.client_list, name="client_list"),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/<int:pk>/edit/", views.client_edit, name="client_edit"),
    path("clients/<int:pk>/delete/", views.client_delete, name="client_delete"),

    # Templates & generation
    path("upload/", views.upload_template, name="upload_template"),
    path("generate/", views.generate_view, name="generate_doc"),
    path("generated/", views.generated_list, name="generated_list"),
    path("download/<int:pk>/", views.download_document, name="download_doc"),
]
