# Django Docx Generator — Full Project Scaffold

Ниже — законченный каркас проекта на **Django 5.x** c **DRF**, **python-docx**, c простым UI и REST API. Скопируйте структуру, установите зависимости и запустите сервер.

---

## Структура проекта
```
docxgen/
├─ manage.py
├─ pyproject.toml            # опционально; можно использовать requirements.txt
├─ requirements.txt
├─ .env.example
├─ docxgen/                  # package настроек Django
│  ├─ __init__.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ asgi.py
└─ core/                     # основное приложение
   ├─ __init__.py
   ├─ admin.py
   ├─ apps.py
   ├─ models.py
   ├─ serializers.py
   ├─ utils.py
   ├─ views.py
   ├─ urls.py
   ├─ forms.py
   ├─ templates/
   │  ├─ base.html
   │  ├─ upload_template.html
   │  ├─ generate_form.html
   │  └─ generated_list.html
   └─ migrations/
      └─ __init__.py
media/
├─ templates/                # загруженные .docx
└─ generated/                # сгенерированные документы

core/management/commands/
└─ values_to_json.py         # команда миграции значений Value → Client.attributes
```

---

## requirements.txt
```txt
Django>=5.0,<6.0
psycopg[binary]>=3.2  # для PostgreSQL; для SQLite не обязателен
python-docx>=1.1.0
Pillow>=10.3.0
djangorestframework>=3.15.2
python-dotenv>=1.0.1
```

---

## pyproject.toml (опционально, если используете pip-tools/uv/poetry — можно пропустить)
```toml
[project]
name = "docxgen"
version = "0.1.0"
dependencies = [
  "Django>=5.0,<6.0",
  "psycopg[binary]>=3.2",
  "python-docx>=1.1.0",
  "Pillow>=10.3.0",
  "djangorestframework>=3.15.2",
  "python-dotenv>=1.0.1",
]
```

---

## .env.example
```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
DATABASE_URL=sqlite:///db.sqlite3
# Для PostgreSQL пример: postgres://user:password@localhost:5432/docxgen
TIME_ZONE=Europe/Helsinki
```

---

## manage.py
```python
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "docxgen.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
```

---

## docxgen/__init__.py
```python
# empty
```

---

## docxgen/asgi.py
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "docxgen.settings")
application = get_asgi_application()
```

---

## docxgen/wsgi.py
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "docxgen.settings")
application = get_wsgi_application()
```

---

## docxgen/settings.py
```python
from pathlib import Path
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "docxgen.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "docxgen.wsgi.application"

# Database via DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
url = urlparse(DATABASE_URL)

if url.scheme.startswith("sqlite"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": url.path if url.path else BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": url.path[1:],
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname,
            "PORT": url.port or 5432,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Helsinki")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}
```

---

## docxgen/urls.py
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),            # простые HTML-страницы
    path("api/", include("core.urls_api")),    # REST API
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## core/apps.py
```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Документы"
```

---

## core/models.py
```python
from django.db import models
from django.utils.translation import gettext_lazy as _


class Entity(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название"))
    key = models.SlugField(
        max_length=64,
        unique=True,
        help_text=_("ID плейсхолдера без фигурных скобок, напр. FIO, ADDRESS"),
        verbose_name=_("Ключ"),
    )

    class Meta:
        verbose_name = _("Сущность")
        verbose_name_plural = _("Сущности")
        ordering = ["key"]

    def __str__(self):
        return f"{self.name} ({{{self.key}}})"

    @property
    def placeholder(self) -> str:
        return f"{{{self.key}}}"


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название/Клиент"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Заметки"))
    # Новое: значения атрибутов клиента хранятся прямо в JSON
    # Пример: {"FIO": "Иванов И.И.", "ADDRESS": "..."}
    attributes = models.JSONField(default=dict, blank=True, verbose_name=_("Атрибуты"))

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ["name"]

    def __str__(self):
        return self.name


# Оставляем модель Value для обратной совместимости (можно удалить после миграции данных)
class Value(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="values")
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="values")
    value = models.TextField(verbose_name=_("Значение"))

    class Meta:
        verbose_name = _("Значение (устар.)")
        verbose_name_plural = _("Значения (устар.)")
        unique_together = ("client", "entity")
        ordering = ["client__name", "entity__key"]

    def __str__(self):
        return f"{self.client} – {self.entity.placeholder} = {self.value}"


class Template(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название шаблона"))
    file = models.FileField(upload_to="templates/", verbose_name=_("Файл .docx"))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Шаблон")
        verbose_name_plural = _("Шаблоны")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.name


class GeneratedDocument(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="generated_docs")
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, related_name="generated_docs")
    file = models.FileField(upload_to="generated/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Сгенерированный документ")
        verbose_name_plural = _("Сгенерированные документы")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client} – {self.template} – {self.created_at:%Y-%m-%d %H:%M}"
```python
from django.db import models
from django.utils.translation import gettext_lazy as _


class Entity(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название"))
    key = models.SlugField(
        max_length=64,
        unique=True,
        help_text=_("ID плейсхолдера без фигурных скобок, напр. FIO, ADDRESS"),
        verbose_name=_("Ключ"),
    )

    class Meta:
        verbose_name = _("Сущность")
        verbose_name_plural = _("Сущности")
        ordering = ["key"]

    def __str__(self):
        return f"{self.name} ({{{self.key}}})"

    @property
    def placeholder(self) -> str:
        return f"{{{self.key}}}"


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название/Клиент"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Заметки"))

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Value(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="values")
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="values")
    value = models.TextField(verbose_name=_("Значение"))

    class Meta:
        verbose_name = _("Значение")
        verbose_name_plural = _("Значения")
        unique_together = ("client", "entity")
        ordering = ["client__name", "entity__key"]

    def __str__(self):
        return f"{self.client} – {self.entity.placeholder} = {self.value}"


class Template(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название шаблона"))
    file = models.FileField(upload_to="templates/", verbose_name=_("Файл .docx"))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Шаблон")
        verbose_name_plural = _("Шаблоны")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.name


class GeneratedDocument(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="generated_docs")
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, related_name="generated_docs")
    file = models.FileField(upload_to="generated/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Сгенерированный документ")
        verbose_name_plural = _("Сгенерированные документы")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client} – {self.template} – {self.created_at:%Y-%m-%d %H:%M}"
```

---

## core/admin.py
```python
from django.contrib import admin
from django import forms
from .models import Entity, Client, Template, GeneratedDocument


class ClientAdminForm(forms.ModelForm):
    """Форма клиента с динамическими полями по всем Entity.
    Каждое поле записывается в JSON client.attributes под ключом Entity.key.
    """
    class Meta:
        model = Client
        fields = ["name", "notes"]  # динамические поля добавим в __init__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing = dict(self.instance.attributes or {})
        self._entity_fields: list[tuple[str, str]] = []  # [(field_name, key)]
        for e in Entity.objects.all().order_by("key"):
            field_name = f"attr__{e.key}"
            self._entity_fields.append((field_name, e.key))
            self.fields[field_name] = forms.CharField(
                label=f"{e.name} ({e.placeholder})",
                required=False,
                initial=existing.get(e.key, ""),
            )

    def clean(self):
        cleaned = super().clean()
        attrs = {}
        for field_name, key in getattr(self, "_entity_fields", []):
            attrs[key] = self.cleaned_data.get(field_name, "") or ""
        self.cleaned_attributes = attrs
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.attributes = getattr(self, "cleaned_attributes", dict(instance.attributes or {}))
        if commit:
            instance.save()
        return instance


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("name", "key")
    search_fields = ("name", "key")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm

    def get_fieldsets(self, request, obj=None):
        base = (None, {"fields": ("name", "notes")})
        dyn = [f"attr__{e.key}" for e in Entity.objects.all().order_by("key")]
        if dyn:
            return (
                base,
                ("Атрибуты", {"fields": tuple(dyn)}),
            )
        return (base,)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "uploaded_at")
    search_fields = ("name",)


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ("client", "template", "file", "created_at")
    list_filter = ("client", "template")
    search_fields = ("client__name", "template__name")
```
python
from django.contrib import admin
from .models import Entity, Client, Value, Template, GeneratedDocument

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("name", "key")
    search_fields = ("name", "key")

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ()
    fieldsets = (
        (None, {"fields": ("name", "notes")}),
        ("Атрибуты", {"fields": ("attributes",)}),
    )

# Value в админке прячем, чтобы не путать пользователей (но модель остаётся в БД)
# admin.site.register(Value)

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "uploaded_at")
    search_fields = ("name",)

@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ("client", "template", "file", "created_at")
    list_filter = ("client", "template")
    search_fields = ("client__name", "template__name")
```python
from django.contrib import admin
from .models import Entity, Client, Value, Template, GeneratedDocument

class ValueInline(admin.TabularInline):
    model = Value
    extra = 0

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("name", "key")
    search_fields = ("name", "key")

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [ValueInline]

@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ("client", "entity", "value")
    list_filter = ("client",)
    search_fields = ("value", "entity__key", "client__name")

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "uploaded_at")
    search_fields = ("name",)

@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ("client", "template", "file", "created_at")
    list_filter = ("client", "template")
    search_fields = ("client__name", "template__name")
```python
from django.contrib import admin
from .models import Entity, Client, Value, Template, GeneratedDocument

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("name", "key")
    search_fields = ("name", "key")

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ("client", "entity", "value")
    list_filter = ("client",)
    search_fields = ("value", "entity__key", "client__name")

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "uploaded_at")
    search_fields = ("name",)

@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ("client", "template", "file", "created_at")
    list_filter = ("client", "template")
    search_fields = ("client__name", "template__name")
```

---

## core/serializers.py
```python
from rest_framework import serializers
from .models import Entity, Client, Value, Template, GeneratedDocument

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["id", "name", "key", "placeholder"]
        read_only_fields = ["placeholder"]

class ClientSerializer(serializers.ModelSerializer):
    # Новое: атрибуты клиента как словарь
    attributes = serializers.JSONField()

    class Meta:
        model = Client
        fields = ["id", "name", "notes", "attributes"]

class ValueSerializer(serializers.ModelSerializer):
    # Оставлено для обратной совместимости API (необязательно использовать)
    entity_key = serializers.ReadOnlyField(source="entity.key")
    client_name = serializers.ReadOnlyField(source="client.name")

    class Meta:
        model = Value
        fields = ["id", "client", "client_name", "entity", "entity_key", "value"]

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ["id", "name", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

class GeneratedDocumentSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source="client.name")
    template_name = serializers.ReadOnlyField(source="template.name")

    class Meta:
        model = GeneratedDocument
        fields = ["id", "client", "client_name", "template", "template_name", "file", "created_at"]
        read_only_fields = ["file", "created_at"]
```python
from rest_framework import serializers
from .models import Entity, Client, Value, Template, GeneratedDocument

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["id", "name", "key", "placeholder"]
        read_only_fields = ["placeholder"]

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "notes"]

class ValueSerializer(serializers.ModelSerializer):
    entity_key = serializers.ReadOnlyField(source="entity.key")
    client_name = serializers.ReadOnlyField(source="client.name")

    class Meta:
        model = Value
        fields = ["id", "client", "client_name", "entity", "entity_key", "value"]

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ["id", "name", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

class GeneratedDocumentSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source="client.name")
    template_name = serializers.ReadOnlyField(source="template.name")

    class Meta:
        model = GeneratedDocument
        fields = ["id", "client", "client_name", "template", "template_name", "file", "created_at"]
        read_only_fields = ["file", "created_at"]
```

---

## core/forms.py (для простых HTML-страниц)
```python
from django import forms
from .models import Template, Client, Entity, Value

class TemplateUploadForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ["name", "file"]

class GenerateForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), label="Клиент")
    template = forms.ModelChoiceField(queryset=Template.objects.all(), label="Шаблон")

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = ["name", "key"]

class ClientAttributesForm(forms.Form):
    """Динамическая форма атрибутов клиента: по всем Entity создаёт поле.
    Все значения сохраняются в client.attributes (JSONfield).
    Также подхватывает устаревшие Value при инициализации.
    """
    def __init__(self, *args, client: Client, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.entities = list(Entity.objects.all().order_by("key"))
        existing_json = dict(getattr(client, "attributes", {}) or {})
        legacy = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
        for ent in self.entities:
            initial = existing_json.get(ent.key, legacy.get(ent.key, ""))
            widget = forms.Textarea(attrs={"rows": 2}) if len(str(initial)) > 120 else forms.TextInput()
            field = forms.CharField(
                label=ent.name,
                required=False,
                initial=initial,
                widget=widget,
            )
            field.widget.attrs.update({
                "data_key": ent.key,
                "data_placeholder": ent.placeholder,
            })
            self.fields[ent.key] = field

    def save(self):
        data = {k: (v or "") for k, v in self.cleaned_data.items()}
        self.client.attributes = data
        self.client.save(update_fields=["attributes"]) 
```python
from django import forms
from .models import Template, Client, Entity, Value

class TemplateUploadForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ["name", "file"]

class GenerateForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), label="Клиент")
    template = forms.ModelChoiceField(queryset=Template.objects.all(), label="Шаблон")


class ClientAttributesForm(forms.Form):
    """Динамическая форма атрибутов клиента: по всем Entity создаёт поле.
    Все значения сохраняются в client.attributes (JSONfield).
    Для обратной совместимости может подтягивать старые Value.
    """
    def __init__(self, *args, client: Client, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.entities = list(Entity.objects.all().order_by("key"))
        existing_json = dict(client.attributes or {})
        # подхватим старые значения Value, если JSON пуст или для конкретного ключа нет значения
        existing_values = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
        for ent in self.entities:
            initial = existing_json.get(ent.key, existing_values.get(ent.key, ""))
            widget = forms.Textarea(attrs={"rows": 2}) if len(str(initial)) > 120 else forms.TextInput()
            self.fields[ent.key] = forms.CharField(
                label=f"{ent.name} ({ent.placeholder})",
                required=False,
                initial=initial,
                widget=widget,
            )

    def save(self):
        data = {k: (v or "") for k, v in self.cleaned_data.items()}
        # Пишем только в JSON у клиента
        self.client.attributes = data
        self.client.save(update_fields=["attributes"])
```
python
from django import forms
from .models import Template, Client, Entity, Value

class TemplateUploadForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ["name", "file"]

class GenerateForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), label="Клиент")
    template = forms.ModelChoiceField(queryset=Template.objects.all(), label="Шаблон")


class ClientAttributesForm(forms.Form):
    """Динамическая форма атрибутов клиента: по всем Entity создаёт поле.
    Сохранение — upsert в таблицу Value.
    """
    def __init__(self, *args, client: Client, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.entities = list(Entity.objects.all().order_by("key"))
        existing = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
        for ent in self.entities:
            initial = existing.get(ent.key, "")
            widget = forms.Textarea(attrs={"rows": 2}) if len(str(initial)) > 120 else forms.TextInput()
            self.fields[ent.key] = forms.CharField(
                label=f"{ent.name} ({ent.placeholder})",
                required=False,
                initial=initial,
                widget=widget,
            )

    def save(self):
        for key, value in self.cleaned_data.items():
            try:
                ent = next(e for e in self.entities if e.key == key)
            except StopIteration:
                continue
            Value.objects.update_or_create(
                client=self.client,
                entity=ent,
                defaults={"value": value or ""},
            )
```python
from django import forms
from .models import Template, Client

class TemplateUploadForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ["name", "file"]

class GenerateForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), label="Клиент")
    template = forms.ModelChoiceField(queryset=Template.objects.all(), label="Шаблон")
```

---

## core/utils.py
```python
import re
import uuid
from pathlib import Path
from docx import Document
from django.conf import settings

PLACEHOLDER_RE = re.compile(r"\{([A-Z0-9_]+)\}")  # {FIO}, {ADDRESS}, ...


def extract_placeholders(doc: Document) -> set[str]:
    """Находит все плейсхолдеры вида {KEY} в параграфах и таблицах."""
    keys = set()
    def scan_text(text: str):
        for m in PLACEHOLDER_RE.finditer(text or ""):
            keys.add(m.group(1))

    for p in doc.paragraphs:
        scan_text(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    scan_text(p.text)
    return keys


def _replace_in_paragraph(paragraph, mapping: dict[str, str]):
    # Простой способ: перезаписываем paragraph.text — может потеряться локальное форматирование внутри абзаца,
    # но для большинства актов/справок подходит. Для полной сохранности форматирования нужен более сложный разбор runs.
    text = paragraph.text
    if not text:
        return
    for key, val in mapping.items():
        text = text.replace(f"{{{key}}}", val)
    paragraph.text = text


def _replace_in_document(doc: Document, mapping: dict[str, str]):
    for p in doc.paragraphs:
        _replace_in_paragraph(p, mapping)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    _replace_in_paragraph(p, mapping)


def generate_document(template_path: str, values_dict: dict[str, str], default_placeholder: str = "—") -> Path:
    """
    Открывает .docx, заменяет {KEY} на значения из values_dict.
    Если значения нет — подставляет default_placeholder (длинное тире по ТЗ).
    Возвращает путь к сохранённому файлу в MEDIA_ROOT/generated/UUID.docx.
    """
    doc = Document(template_path)

    # какие ключи реально есть в шаблоне
    present_keys = extract_placeholders(doc)

    # формируем mapping: только для встреченных ключей
    mapping = {key: str(values_dict.get(key, default_placeholder)) for key in present_keys}

    _replace_in_document(doc, mapping)

    out_dir = Path(settings.MEDIA_ROOT) / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{uuid.uuid4().hex}.docx"
    doc.save(out_path)
    return out_path
```

---

## core/views.py
```python
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib import messages

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Entity, Client, Value, Template, GeneratedDocument
from .serializers import (
    EntitySerializer, ClientSerializer, ValueSerializer,
    TemplateSerializer, GeneratedDocumentSerializer
)
from .forms import TemplateUploadForm, GenerateForm, ClientAttributesForm, ClientForm, EntityForm
from .utils import generate_document

# ---------- HTML Views ----------

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
    temp_client = Client()  # чтобы отрисовать форму атрибутов
    attrs_form = ClientAttributesForm(request.POST or None, client=temp_client)
    if request.method == "POST" and client_form.is_valid():
        client = client_form.save()
        attrs_form = ClientAttributesForm(request.POST, client=client)
        if attrs_form.is_valid():
            attrs_form.save()
        messages.success(request, "Клиент создан")
        return redirect("client_list")
    return render(request, "client_form.html", {"client_form": client_form, "attrs_form": attrs_form})

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
```python
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib import messages

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Entity, Client, Value, Template, GeneratedDocument
from .serializers import (
    EntitySerializer, ClientSerializer, ValueSerializer,
    TemplateSerializer, GeneratedDocumentSerializer
)
from .forms import TemplateUploadForm, GenerateForm, ClientAttributesForm
from .utils import generate_document

# ---------- HTML Views ----------

def index(request):
    return render(request, "home.html")


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


def client_list(request):
    return render(request, "client_list.html", {"clients": Client.objects.all().order_by("name")})


def client_attributes(request, pk: int):
    client = get_object_or_404(Client, pk=pk)
    form = ClientAttributesForm(request.POST or None, client=client)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Атрибуты клиента сохранены")
        return redirect("client_list")
    return render(request, "client_attributes_form.html", {"client": client, "form": form})


def generate_view(request):
    if request.method == "POST":
        form = GenerateForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data["client"]
            template = form.cleaned_data["template"]

            # Значения теперь берём из client.attributes; при желании можно подхватить старые Value
            attrs = dict(client.attributes or {})
            values = attrs  # ключи уже такие же, как у плейсхолдеров

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
        # Сохраняем только ключи из Entity (чтобы не плодить лишнее)
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
```python
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib import messages

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Entity, Client, Value, Template, GeneratedDocument
from .serializers import (
    EntitySerializer, ClientSerializer, ValueSerializer,
    TemplateSerializer, GeneratedDocumentSerializer
)
from .forms import TemplateUploadForm, GenerateForm, ClientAttributesForm
from .utils import generate_document

# ---------- HTML Views (простые страницы) ----------

def index(request):
    return render(request, "home.html")


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


def client_list(request):
    return render(request, "client_list.html", {"clients": Client.objects.all().order_by("name")})


def client_attributes(request, pk: int):
    client = get_object_or_404(Client, pk=pk)
    form = ClientAttributesForm(request.POST or None, client=client)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Атрибуты клиента сохранены")
        return redirect("client_list")
    return render(request, "client_attributes_form.html", {"client": client, "form": form})


def generate_view(request):
    if request.method == "POST":
        form = GenerateForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data["client"]
            template = form.cleaned_data["template"]

            values = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
            out_path = generate_document(template.file.path, values)

            # Сохраняем в FileField относительный путь ОТНОСИТЕЛЬНО MEDIA_ROOT
            rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
            gd = GeneratedDocument.objects.create(client=client, template=template)
            gd.file.name = Path(rel).as_posix()
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
            data = {}
            for e in Entity.objects.all():
                val = Value.objects.filter(client=client, entity=e).values_list("value", flat=True).first() or ""
                data[e.key] = val
            return Response(data)
        # PUT — массовое сохранение атрибутов {key: value}
        payload = request.data or {}
        updated = {}
        for key, val in payload.items():
            try:
                e = Entity.objects.get(key=key)
            except Entity.DoesNotExist:
                continue
            Value.objects.update_or_create(client=client, entity=e, defaults={"value": val or ""})
            updated[key] = val
        return Response({"updated": updated})

class ValueViewSet(viewsets.ModelViewSet):
    queryset = Value.objects.select_related("client", "entity").all()
    serializer_class = ValueSerializer

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

    values = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
    out_path = generate_document(template.file.path, values)

    # Сохраняем относительный путь к MEDIA_ROOT в FileField
    rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
    gd = GeneratedDocument.objects.create(client=client, template=template)
    gd.file.name = Path(rel).as_posix()
    gd.save()

    if request.query_params.get("download") == "1":
        return FileResponse(open(gd.file.path, "rb"), as_attachment=True, filename=f"{client.name}.docx")

    serializer = GeneratedDocumentSerializer(gd)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```python
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib import messages

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Entity, Client, Value, Template, GeneratedDocument
from .serializers import (
    EntitySerializer, ClientSerializer, ValueSerializer,
    TemplateSerializer, GeneratedDocumentSerializer
)
from .forms import TemplateUploadForm, GenerateForm
from .utils import generate_document

# ---------- HTML Views (простые страницы) ----------

def index(request):
    return render(request, "base.html")


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

            # собрать словарь значений для клиента
            values = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
            out_path = generate_document(template.file.path, values)

            # Сохраняем в FileField относительный путь ОТНОСИТЕЛЬНО MEDIA_ROOT
            rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
            gd = GeneratedDocument.objects.create(client=client, template=template)
            gd.file.name = str(rel).replace("\", "/")  # например: 'generated/uuid.docx'
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

class ValueViewSet(viewsets.ModelViewSet):
    queryset = Value.objects.select_related("client", "entity").all()
    serializer_class = ValueSerializer

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

    values = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
    out_path = generate_document(template.file.path, values)

    # Сохраняем относительный путь к MEDIA_ROOT в FileField
    rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
    gd = GeneratedDocument.objects.create(client=client, template=template)
    gd.file.name = str(rel).replace("\", "/")
    gd.save()

    if request.query_params.get("download") == "1":
        return FileResponse(open(gd.file.path, "rb"), as_attachment=True, filename=f"{client.name}.docx")

    serializer = GeneratedDocumentSerializer(gd)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```python
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.urls import reverse
from django.contrib import messages

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Entity, Client, Value, Template, GeneratedDocument
from .serializers import (
    EntitySerializer, ClientSerializer, ValueSerializer,
    TemplateSerializer, GeneratedDocumentSerializer
)
from .forms import TemplateUploadForm, GenerateForm
from .utils import generate_document

# ---------- HTML Views (простые страницы) ----------

def index(request):
    return render(request, "base.html")


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

            # собрать словарь значений для клиента
            values = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
            out_path = generate_document(template.file.path, values)

            # сохраняем в FileField относительный путь ОТНОСИТЕЛЬНО MEDIA_ROOT
            from django.conf import settings
            from pathlib import Path
            rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())

            gd = GeneratedDocument.objects.create(client=client, template=template)
            gd.file.name = str(rel).replace("\", "/")  # нормализуем слеши для совместимости
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
        raise Http404
    return FileResponse(open(doc.file.path, "rb"), as_attachment=True, filename=f"{doc.client.name}.docx")


# ---------- REST API ----------

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ValueViewSet(viewsets.ModelViewSet):
    queryset = Value.objects.select_related("client", "entity").all()
    serializer_class = ValueSerializer

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

    values = {v.entity.key: v.value for v in Value.objects.filter(client=client).select_related("entity")}
    out_path = generate_document(template.file.path, values)

    # сохраняем относительный путь к MEDIA_ROOT
    from django.conf import settings
    from pathlib import Path
    rel = Path(out_path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())

    gd = GeneratedDocument.objects.create(client=client, template=template)
    gd.file.name = str(rel).replace("\", "/")
    gd.save()

    if request.query_params.get("download") == "1":
        return FileResponse(open(gd.file.path, "rb"), as_attachment=True, filename=f"{client.name}.docx")

    serializer = GeneratedDocumentSerializer(gd)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

## core/urls.py (HTML)
```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # Entities
    path("entities/", views.entity_list, name="entities_list"),
    path("entities/create/", views.entity_create, name="entity_create"),

    # Clients
    path("clients/", views.client_list, name="client_list"),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/<int:pk>/attributes/", views.client_attributes, name="client_attributes"),

    # Templates & generation
    path("upload/", views.upload_template, name="upload_template"),
    path("generate/", views.generate_view, name="generate_doc"),
    path("generated/", views.generated_list, name="generated_list"),
    path("download/<int:pk>/", views.download_document, name="download_doc"),
]
```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_template, name="upload_template"),
    path("generate/", views.generate_view, name="generate_doc"),
    path("generated/", views.generated_list, name="generated_list"),
    path("download/<int:pk>/", views.download_document, name="download_doc"),

    # Новые страницы для клиентов и их атрибутов
    path("clients/", views.client_list, name="client_list"),
    path("clients/<int:pk>/attributes/", views.client_attributes, name="client_attributes"),
]
```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_template, name="upload_template"),
    path("generate/", views.generate_view, name="generate_doc"),
    path("generated/", views.generated_list, name="generated_list"),
    path("download/<int:pk>/", views.download_document, name="download_doc"),
]
```

---

## core/urls_api.py (REST API)
```python
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
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EntityViewSet, ClientViewSet, ValueViewSet,
    TemplateViewSet, GeneratedDocumentViewSet,
    api_generate,
)

router = DefaultRouter()
router.register(r"entities", EntityViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"values", ValueViewSet)
router.register(r"templates", TemplateViewSet)
router.register(r"generated", GeneratedDocumentViewSet, basename="generated")

urlpatterns = [
    path("", include(router.urls)),
    path("generate/<int:client_id>/<int:template_id>/", api_generate, name="api_generate"),
]
```

---

## core/templates/base.html
```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocxGen</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <style>
    /* контейнер и карточки во всю ширину */
    .container{width:100%;max-width:none;padding-inline:12px;margin-inline:auto}
    .card{width:100%;padding:1.25rem;border:1px solid #e5e7eb;border-radius:14px;background:#fff;overflow:hidden}
    .card--full{padding:0}
    header.topbar{display:flex;justify-content:space-between;align-items:center;margin:1rem 0}

    /* таблицы */
    .table-wrapper{width:100%;overflow-x:auto}
    .table-fixed{table-layout:fixed;width:100%}
    .table-entities{font-size:13.5px}
    .table-entities col.c-name{width:52%}
    .table-entities col.c-key{width:22%}
    .table-entities col.c-placeholder{width:18%}
    .table-entities col.c-actions{width:8%}

    .table-clients{font-size:14px}
    .table-clients col.c-name{width:60%}
    .table-clients col.c-count{width:20%}
    .table-clients col.c-actions{width:20%}

    .table-generated{font-size:13.5px}
    .table-generated col.c-date{width:20%}
    .table-generated col.c-client{width:30%}
    .table-generated col.c-template{width:32%}
    .table-generated col.c-actions{width:18%}

    table td, table th{vertical-align:middle}

    /* текст и переносы */
    .wrap{overflow-wrap:anywhere;word-break:break-word}
    .clamp-2{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
    .monospace{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace}
    .pill{display:inline-block;max-width:100%;overflow:hidden;text-overflow:ellipsis;vertical-align:middle;border-radius:999px;padding:2px 8px;background:#eef2ff;color:#3730a3;font-size:12px;border:1px solid #c7d2fe}

    /* действия и кнопки */
    .actions-col{text-align:right}
    .action-stack{display:flex;flex-direction:column;align-items:flex-end;gap:6px}
    .btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:6px 10px;border-radius:10px;border:1px solid transparent;text-decoration:none;font-weight:600;transition:all .15s}
    .btn-sm{font-size:12px;line-height:1}
    .btn-primary{background:#2563eb;color:#fff;border-color:#1d4ed8}
    .btn-primary:hover{background:#1d4ed8}
    .btn-outline{background:transparent;border-color:#e5e7eb;color:#374151}
    .btn-danger{color:#b91c1c;border-color:#fecaca}
    .btn-outline.btn-danger:hover{background:#fee2e2}

    /* тулбары */
    .toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
    .toolbar .spacer{flex:1}
  </style>
</head>
<body>
  <main class="container">
    <header class="topbar">
      <strong>DocxGen</strong>
      <nav>
        <ul>
          <li><a href="/clients/">Клиенты</a></li>
          <li><a href="/entities/">Атрибуты (Entity)</a></li>
          <li><a href="/upload/">Шаблоны</a></li>
          <li><a href="/generate/">Генерация</a></li>
          <li><a href="/generated/">Готовые</a></li>
          <li><a href="/admin/" target="_blank">Admin</a></li>
        </ul>
      </nav>
    </header>

    {% if messages %}
      <article class="card" style="background:#f8fafc">
        <ul>{% for m in messages %}<li>{{ m }}</li>{% endfor %}</ul>
      </article>
    {% endif %}

    {% block content %}{% endblock %}
  </main>
</body>
</html>
```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocxGen</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
  <main class="container">
    <nav>
      <ul>
        <li><strong>DocxGen</strong></li>
      </ul>
      <ul>
        <li><a href="/clients/">Клиенты</a></li>
        <li><a href="/upload/">Загрузить шаблон</a></li>
        <li><a href="/generate/">Сгенерировать</a></li>
        <li><a href="/generated/">Готовые документы</a></li>
        <li><a href="/admin/" target="_blank">Admin</a></li>
      </ul>
    </nav>
    <hr>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocxGen</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
  <main class="container">
    <nav>
      <ul>
        <li><strong>DocxGen</strong></li>
      </ul>
      <ul>
        <li><a href="/clients/">Клиенты</a></li>
        <li><a href="/upload/">Загрузить шаблон</a></li>
        <li><a href="/generate/">Сгенерировать</a></li>
        <li><a href="/generated/">Готовые документы</a></li>
        <li><a href="/admin/" target="_blank">Admin</a></li>
      </ul>
    </nav>
    <hr>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocxGen</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
  <main class="container">
    <nav>
      <ul>
        <li><strong>DocxGen</strong></li>
      </ul>
      <ul>
        <li><a href="/upload/">Загрузить шаблон</a></li>
        <li><a href="/generate/">Сгенерировать</a></li>
        <li><a href="/generated/">Готовые документы</a></li>
        <li><a href="/admin/" target="_blank">Admin</a></li>
      </ul>
    </nav>
    <hr>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

---

## core/templates/upload_template.html
```html
{% extends 'base.html' %}
{% block content %}
<article class="card">
  <h2 style="margin-top:0">Загрузка шаблона (.docx)</h2>
  <form method="post" enctype="multipart/form-data" class="toolbar">
    {% csrf_token %}
    {{ form.as_p }}
    <span class="spacer"></span>
    <button type="submit" class="btn btn-primary btn-sm">Загрузить</button>
  </form>
</article>

<article class="card card--full" style="margin-top:1rem">
  <header style="padding:1rem 1.25rem"><h3 style="margin:0">Загруженные шаблоны</h3></header>
  <div class="table-wrapper">
    <table class="table-fixed" style="font-size:13.5px">
      <colgroup>
        <col style="width:50%"><col style="width:30%"><col style="width:20%">
      </colgroup>
      <thead><tr><th>Название</th><th>Файл</th><th>Загружен</th></tr></thead>
      <tbody>
        {% for t in templates %}
        <tr>
          <td class="wrap"><div class="clamp-2" title="{{ t.name }}">{{ t.name|truncatechars:100 }}</div></td>
          <td><a href="{{ t.file.url }}" class="btn btn-outline btn-sm">Скачать</a></td>
          <td>{{ t.uploaded_at }}</td>
        </tr>
        {% empty %}
        <tr><td colspan="3">Пока нет шаблонов</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</article>
{% endblock %}
```html
{% extends 'base.html' %}
{% block content %}
<h2>Загрузка шаблона (.docx)</h2>
<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Загрузить</button>
</form>

<h3>Загруженные шаблоны</h3>
<table>
  <thead><tr><th>Название</th><th>Файл</th><th>Загружен</th></tr></thead>
  <tbody>
  {% for t in templates %}
    <tr>
      <td>{{ t.name }}</td>
      <td><a href="{{ t.file.url }}">скачать</a></td>
      <td>{{ t.uploaded_at }}</td>
    </tr>
  {% empty %}
    <tr><td colspan="3">Пока нет шаблонов</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
```html
{% extends 'base.html' %}
{% block content %}
<h2>Загрузка шаблона (.docx)</h2>
<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Загрузить</button>
</form>

<h3>Загруженные шаблоны</h3>
<table>
  <thead><tr><th>Название</th><th>Файл</th><th>Загружен</th></tr></thead>
  <tbody>
  {% for t in templates %}
    <tr>
      <td>{{ t.name }}</td>
      <td><a href="{{ t.file.url }}">скачать</a></td>
      <td>{{ t.uploaded_at }}</td>
    </tr>
  {% empty %}
    <tr><td colspan="3">Пока нет шаблонов</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
```

---

## core/templates/generate_form.html
```html
{% extends 'base.html' %}
{% block content %}
<form method="post" class="card">
  {% csrf_token %}
  <h2 style="margin-top:0">Генерация документа</h2>
  <div style="display:grid;grid-template-columns:1fr;gap:12px">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <label>Клиент: {{ form.client }}</label>
      <label>Шаблон: {{ form.template }}</label>
    </div>
  </div>
  <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px">
    <button type="submit" class="btn btn-primary">Сгенерировать</button>
  </div>
  <p class="wrap" style="margin:.5rem 0 0;color:#6b7280">Подсказка: создайте атрибуты (Entity) и заполните их у клиента — значения подставятся автоматически.</p>
</form>
{% endblock %}
```html
{% extends 'base.html' %}
{% block content %}
<h2>Генерация документа</h2>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Сгенерировать</button>
</form>
<p>
  Подсказка: создайте сущности (например FIO, ADDRESS), затем на странице <a href="/clients/">Клиенты</a> откройте клиента и заполните атрибуты.
</p>
{% endblock %}
```html
{% extends 'base.html' %}
{% block content %}
<h2>Генерация документа</h2>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Сгенерировать</button>
</form>
<p>
  Подсказка: создайте сущности (например FIO, ADDRESS), затем в админке задайте значения для клиента.
</p>
{% endblock %}
```

---

## core/templates/generated_list.html
```html
{% extends 'base.html' %}
{% block content %}
<article class="card card--full">
  <header style="padding:1rem 1.25rem"><h2 style="margin:0">Готовые документы</h2></header>
  <div class="table-wrapper">
    <table class="table-fixed table-generated">
      <colgroup>
        <col class="c-date"><col class="c-client"><col class="c-template"><col class="c-actions">
      </colgroup>
      <thead><tr><th>Дата</th><th>Клиент</th><th>Шаблон</th><th class="actions-col">Действия</th></tr></thead>
      <tbody>
      {% for d in docs %}
        <tr>
          <td>{{ d.created_at }}</td>
          <td class="wrap"><div class="clamp-2" title="{{ d.client.name }}">{{ d.client.name|truncatechars:80 }}</div></td>
          <td class="wrap"><div class="clamp-2" title="{{ d.template.name }}">{{ d.template.name|truncatechars:80 }}</div></td>
          <td class="actions-col">
            <div class="action-stack">
              <a href="/download/{{ d.id }}/" class="btn btn-primary btn-sm">Скачать</a>
            </div>
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="4">Пока нет документов</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</article>
{% endblock %}
```html
{% extends 'base.html' %}
{% block content %}
<h2>Готовые документы</h2>
<table>
  <thead><tr><th>Дата</th><th>Клиент</th><th>Шаблон</th><th>Файл</th></tr></thead>
  <tbody>
  {% for d in docs %}
    <tr>
      <td>{{ d.created_at }}</td>
      <td>{{ d.client.name }}</td>
      <td>{{ d.template.name }}</td>
      <td><a href="/download/{{ d.id }}/">Скачать</a></td>
    </tr>
  {% empty %}
    <tr><td colspan="4">Пока нет документов</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
```html
{% extends 'base.html' %}
{% block content %}
<h2>Готовые документы</h2>
<table>
  <thead><tr><th>Дата</th><th>Клиент</th><th>Шаблон</th><th>Файл</th></tr></thead>
  <tbody>
  {% for d in docs %}
    <tr>
      <td>{{ d.created_at }}</td>
      <td>{{ d.client.name }}</td>
      <td>{{ d.template.name }}</td>
      <td><a href="/download/{{ d.id }}/">Скачать</a></td>
    </tr>
  {% empty %}
    <tr><td colspan="4">Пока нет документов</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
```

---

## Инструкции по запуску

### Обновление под новую модель атрибутов
Теперь значения атрибутов хранятся внутри `Client.attributes` (JSON). Старые записи в `Value` можно перенести и перестать использовать.

1) Примените миграции для добавления поля JSON:
```bash
python manage.py makemigrations core
python manage.py migrate
```

2) (Опционально) Перенести старые `Value` в JSON — добавлена команда:
```
python manage.py values_to_json
```
Она аккуратно сольёт пары (Entity.key → Value.value) в `client.attributes`.

3) После проверки можете вручную удалить модель `Value` (удалить код модели и выполнить `makemigrations`/`migrate`). Пока что модель оставлена для совместимости, но интерфейсы приложения её не используют.

### Дальше стандартно
```bash
python manage.py runserver
```
- Заполняйте атрибуты клиента на странице **Клиенты → Атрибуты**.
- Генерация как прежде: выбрать клиента и шаблон.

---

## core/management/commands/values_to_json.py
```python
from django.core.management.base import BaseCommand
from core.models import Client, Value

class Command(BaseCommand):
    help = "Переносит значения из Value в JSON-поле Client.attributes"

    def handle(self, *args, **options):
        moved_clients = 0
        for client in Client.objects.all():
            attrs = dict(client.attributes or {})
            changed = False
            for v in Value.objects.filter(client=client).select_related("entity"):
                key = v.entity.key
                if attrs.get(key) != v.value:
                    attrs[key] = v.value or ""
                    changed = True
            if changed:
                client.attributes = attrs
                client.save(update_fields=["attributes"])
                moved_clients += 1
        self.stdout.write(self.style.SUCCESS(f"Готово. Обновлено клиентов: {moved_clients}"))
```



## core/templates/client_form.html
```html
{% extends 'base.html' %}
{% block content %}
<form method="post" class="card wrap">
  {% csrf_token %}
  <h2 style="margin:0 0 .5rem 0;">Новый клиент</h2>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start">
    <section>
      <label>Название/Клиент
        {{ client_form.name }}
      </label>
      <label>Заметки
        {{ client_form.notes }}
      </label>
    </section>

    <section>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:.5rem">
        <h3 style="margin:0">Атрибуты</h3>
        <span class="pill">Всего: {{ attrs_form.fields|length }}</span>
        <span class="spacer"></span>
      </div>
      <div class="field" style="margin-bottom:.5rem">
        <label for="attrSearch">Поиск по атрибутам</label>
        <input id="attrSearch" type="search" placeholder="Начните вводить название или ключ...">
        <label style="display:flex;align-items:center;gap:.5rem;margin:.5rem 0 0 0">
          <input type="checkbox" id="toggleKeys" checked>
          <span class="muted">Показывать технические ключи</span>
        </label>
      </div>

      <div style="display:grid;grid-template-columns:repeat(2,minmax(260px,1fr));gap:12px">
        {% for f in attrs_form %}
          <div class="attr-field wrap" data-label="{{ f.label|lower }} {{ f.field.widget.attrs.data_key|lower }}">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
              <label for="{{ f.id_for_label }}" style="margin:0">{{ f.label }}</label>
              <span class="pill monospace token-pill">{{ f.field.widget.attrs.data_placeholder }}</span>
            </div>
            {{ f }}
          </div>
        {% endfor %}
      </div>
    </section>
  </div>

  <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px">
    <a href="/clients/" role="button" class="btn btn-outline">Отмена</a>
    <button type="submit" class="btn btn-primary">Создать клиента</button>
  </div>
</form>
<script>
  document.addEventListener('DOMContentLoaded', function(){
    const q = document.getElementById('attrSearch');
    const toggle = document.getElementById('toggleKeys');
    const items = Array.from(document.querySelectorAll('.attr-field'));
    const pills = Array.from(document.querySelectorAll('.token-pill'));
    function applyFilter(){
      const term = (q?.value || '').toLowerCase().trim();
      items.forEach(el => {
        const label = (el.dataset.label || '').toLowerCase();
        el.style.display = term === '' || label.includes(term) ? '' : 'none';
      });
    }
    q && q.addEventListener('input', applyFilter); applyFilter();
    function applyToggle(){
      const on = toggle?.checked; pills.forEach(p => p.style.display = on ? '' : 'none');
    }
    toggle && toggle.addEventListener('change', applyToggle); applyToggle();
  });
</script>
{% endblock %}
```

## core/templates/entity_form.html
```html
{% extends 'base.html' %}
{% block content %}
<form method="post" class="card">
  {% csrf_token %}
  <h2 style="margin-top:0">Новый атрибут</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <label>Название
      {{ form.name }}
    </label>
    <label>Ключ (без фигурных скобок)
      {{ form.key }}
    </label>
  </div>
  <p class="muted" style="margin:.5rem 0 0">Плейсхолдер будет вида <span class="pill monospace">{KEY}</span>.</p>
  <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px">
    <a href="/entities/" class="btn btn-outline">Отмена</a>
    <button type="submit" class="btn btn-primary">Создать атрибут</button>
  </div>
</form>
{% endblock %}
```

