from django import forms
from .models import Template, Client, Entity  # <-- без Value

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
    Значения берём только из client.attributes (без модели Value).
    """
    def __init__(self, *args, client: Client, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.entities = list(Entity.objects.all().order_by("key"))
        existing_json = dict(getattr(client, "attributes", {}) or {})

        for ent in self.entities:
            initial = existing_json.get(ent.key, "")
            widget = forms.Textarea(attrs={"rows": 2}) if len(str(initial)) > 120 else forms.TextInput()
            field = forms.CharField(
                label=ent.name,          # показываем только человекочитаемое имя
                required=False,
                initial=initial,
                widget=widget,
            )
            # прокидываем мета для шаблона (бейдж {KEY})
            field.widget.attrs.update({
                "data_key": ent.key,
                "data_placeholder": ent.placeholder,
            })
            self.fields[ent.key] = field

    def save(self):
        data = {k: (v or "") for k, v in self.cleaned_data.items()}
        self.client.attributes = data
        self.client.save(update_fields=["attributes"])
