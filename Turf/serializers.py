from rest_framework import serializers
from Turf.models import TurfDb,bookingDb

class Turf_Serializer(serializers.ModelSerializer):
    class Meta:
        model=TurfDb
        fields="__all__"
        read_only_field=["id"]
class Booking_Serializer(serializers.ModelSerializer):
    class Meta:
        model=bookingDb
        fields="__all__"
        read_only_field=["id"]