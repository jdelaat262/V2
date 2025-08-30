from rest_framework import serializers
from .models import Cursus, Deelnemer

class CursusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cursus
        fields = '__all__'

class DeelnemerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deelnemer
        fields = '__all__'