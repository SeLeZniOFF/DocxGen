from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib import messages

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Entity, Client, Template, GeneratedDocument
from .serializers import (
    EntitySerializer, ClientSerializer, ValueSerializer,
    TemplateSerializer, GeneratedDocumentSerializer
)
from .forms import TemplateUploadForm, GenerateForm, ClientAttributesForm, ClientForm, EntityForm
from .utils import generate_document

# ---------- HTML Views ----------
def entity_edit(request, pk: int):
    entity = get_object_or_404(Entity, pk=pk)
    form = EntityForm(request.POST or None, instance=entity)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Атрибут обновлён")
        return redirect("entities_list")
    return render(request, "entity_form.html", {"form": form, "mode": "edit", "entity": entity})

def entity_delete(request, pk: int):
    entity = get_object_or_404(Entity, pk=pk)
    if request.method == "POST":
        entity.delete()
        messages.success(request, "Атрибут удалён")
        return redirect("entities_list")
    return render(request, "confirm_delete.html", {"title": "Удалить атрибут", "object": entity, "cancel_url": "entities"})

def client_edit(request, pk: int):
    client = get_object_or_404(Client, pk=pk)
    client_form = ClientForm(requestPOST := request.POST or None, instance=client)
    attrs_form = ClientAttributesForm(requestPOST, client=client)
    if request.method == "POST" and client_form.is_valid() and attrs_form.is_valid():
        client_form.save()
        attrs_form.save()
        messages.success(request, "Клиент обновлён")
        return redirect("client_list")
    return render(request, "client_form.html", {
        "client_form": client_form, "attrs_form": attrs_form, "mode": "edit", "client": client
    })
def client_delete(request, pk: int):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        messages.success(request, "Клиент удалён")
        return redirect("client_list")
    return render(request, "confirm_delete.html", {"title": "Удалить клиента", "object": client, "cancel_url": "clients"})

def index(request):
    stats = {
        "clients": Client.objects.count(),
        "entities": Entity.objects.count(),
        "templates": Template.objects.count(),
        "docs": GeneratedDocument.objects.count(),
    }
    return render(request, "home.html", {"stats": stats})

# --- Entities UI ---

def entity_list(request):
    entities = Entity.objects.all().order_by("key")
    return render(request, "entities_list.html", {"entities": entities})

def entity_create(request):
    form = EntityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Атрибут добавлен")
        return redirect("entities_list")
    return render(request, "entity_form.html", {"form": form})

# --- Clients UI ---

def client_list(request):
    total_entities = Entity.objects.count()
    return render(request, "client_list.html", {
        "clients": Client.objects.all().order_by("name"),
        "total_entities": total_entities,
    })

def client_create(request):
    client_form = ClientForm(request.POST or None)
    temp_client = Client()
    attrs_form = ClientAttributesForm(request.POST or None, client=temp_client)
    if request.method == "POST" and client_form.is_valid():
        client = client_form.save()
        attrs_form = ClientAttributesForm(request.POST, client=client)
        if attrs_form.is_valid():
            attrs_form.save()
        messages.success(request, "Клиент создан")
        return redirect("client_list")
    return render(request, "client_form.html", {
        "client_form": client_form, "attrs_form": attrs_form, "mode": "create"
    })
# --- Templates & Generation ---

def upload_template(request):
    if request.method == "POST":
        form = TemplateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Шаблон загружен!")
            return redirect("upload_template")
    else:
        form = TemplateUploadForm()
    return render(request, "upload_template.html", {"form": form, "templates": Template.objects.all()})


def generate_view(request):
    if request.method == "POST":
        form = GenerateForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data["client"]
            template = form.cleaned_data["template"]
            values = dict(client.attributes or {})
            out_path = generate_document(template.file.path, values)
            rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
            gd = GeneratedDocument.objects.create(client=client, template=template)
            gd.file.name = rel.as_posix()
            gd.save()
            messages.success(request, "Документ сгенерирован!")
            return redirect("generated_list")
    else:
        form = GenerateForm()
    return render(request, "generate_form.html", {"form": form})


def generated_list(request):
    return render(request, "generated_list.html", {"docs": GeneratedDocument.objects.select_related("client", "template")})


def download_document(request, pk: int):
    doc = get_object_or_404(GeneratedDocument, pk=pk)
    if not doc.file:
        raise Http404("Файл не найден")
    return FileResponse(open(doc.file.path, "rb"), as_attachment=True, filename=f"{doc.client.name}.docx")

# ---------- REST API ----------

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    @action(detail=True, methods=["get", "put"], url_path="attributes")
    def attributes(self, request, pk=None):
        client = self.get_object()
        if request.method == "GET":
            return Response(client.attributes or {})
        payload = request.data or {}
        valid_keys = set(Entity.objects.values_list("key", flat=True))
        client.attributes = {k: (v or "") for k, v in payload.items() if k in valid_keys}
        client.save(update_fields=["attributes"])
        return Response(client.attributes)

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

class GeneratedDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedDocument.objects.select_related("client", "template").all()
    serializer_class = GeneratedDocumentSerializer

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        doc = self.get_object()
        return FileResponse(open(doc.file.path, "rb"), as_attachment=True, filename=f"{doc.client.name}.docx")

@api_view(["POST"])  # /api/generate/<client_id>/<template_id>/
def api_generate(request, client_id: int, template_id: int):
    client = get_object_or_404(Client, pk=client_id)
    template = get_object_or_404(Template, pk=template_id)
    values = dict(client.attributes or {})
    out_path = generate_document(template.file.path, values)
    rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
    gd = GeneratedDocument.objects.create(client=client, template=template)
    gd.file.name = rel.as_posix()
    gd.save()
    if request.query_params.get("download") == "1":
        return FileResponse(open(gd.file.path, "rb"), as_attachment=True, filename=f"{client.name}.docx")
    serializer = GeneratedDocumentSerializer(gd)
    return Response(serializer.data, status=status.HTTP_201_CREATED)