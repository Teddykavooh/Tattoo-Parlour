from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Artist, Service
from .serializers import (
    ArtistSerializer,
    ServiceSerializer,
)

# Create your views here.
class ArtistListView(ListAPIView):
    """
    Returns all active artists.
    Public endpoint.
    """

    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]

    queryset = Artist.objects.filter(
        is_active=True
    ).order_by("name")


class ServiceListView(ListAPIView):
    """
    Returns all active services.
    Public endpoint.
    """

    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    queryset = Service.objects.filter(
        is_active=True
    ).order_by("name")