# registrations/serializers.py
from rest_framework import serializers
from .models import Registration, AdmissionTicket

class AdmissionTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionTicket
        fields = ['id', 'ticket_number', 'pdf_file_path', 'generated_at']

class RegistrationSerializer(serializers.ModelSerializer):
    ticket = AdmissionTicketSerializer(read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'user', 'user_name', 'exam_name', 'status', 'applied_at', 'remarks', 'ticket']
        read_only_fields = ['status', 'applied_at', 'user']