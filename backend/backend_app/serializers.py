from rest_framework import serializers
from .models import Cursus, Deelnemer, QREvent, QRDeelnemer

class CursusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cursus
        fields = '__all__'

class DeelnemerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deelnemer
        fields = '__all__'

class QREventSerializer(serializers.ModelSerializer):
    class Meta:
        model = QREvent
        fields = '__all__'

class QRDeelnemerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRDeelnemer
        fields = '__all__'