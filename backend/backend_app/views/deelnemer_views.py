from rest_framework import viewsets
from ..models import Deelnemer
from ..serializers import DeelnemerSerializer


class DeelnemerViewSet(viewsets.ModelViewSet):
    queryset = Deelnemer.objects.all()
    serializer_class = DeelnemerSerializer