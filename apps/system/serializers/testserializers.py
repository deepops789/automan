from rest_framework import serializers
from system.models import faker_data

class FakerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = faker_data
        fields = ['id', 'name', 'created_at']
