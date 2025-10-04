from django.contrib import admin
from django import forms
from .models import Entity, Client, Template, GeneratedDocument


class ClientAdminForm(forms.ModelForm):
    """
    Динамическая форма клиента: для каждого Entity создаёт отдельное поле
    (attr__<KEY>). Значения сохраняются в Client.attributes (JSON).
    """
    class Meta:
        model = Client
        fields = ["name", "notes"]  # JSON редактируем через динамические поля

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing = dict(self.instance.attributes or {})
        self._entity_fields: list[tuple[str, str]] = []  # (field_name, key)

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
        # сохраняем подготовленный словарь для save()
        self.cleaned_attributes = attrs
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # пишем значения строго из динамических полей
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

    # ВАЖНО: отдаём форму напрямую, чтобы админка не пыталась «ограничить»
    # поля по fieldsets и не ругалась на attr__KEY
    def get_form(self, request, obj=None, change=False, **kwargs):
        return self.form

    # Рисуем секции: базовые поля + динамические «Атрибуты»
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
