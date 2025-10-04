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