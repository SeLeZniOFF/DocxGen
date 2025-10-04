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