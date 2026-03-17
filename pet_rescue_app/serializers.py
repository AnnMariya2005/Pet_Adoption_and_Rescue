from rest_framework import serializers
from .models import PetReport, Notification


class PetReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = PetReport
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'