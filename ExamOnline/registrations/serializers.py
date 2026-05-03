from rest_framework import serializers
from .models import Registration, AdmissionTicket
from exam.serializers import ExamSerializer
from user.serializers import StudentSerializer

class RegistrationSerializer(serializers.ModelSerializer):
    exam_info = ExamSerializer(source='exam', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Registration
        fields = '__all__'
        read_only_fields = ('student', 'status', 'apply_time', 'review_time')


class AdmissionTicketSerializer(serializers.ModelSerializer):
    registration_info = RegistrationSerializer(source='registration', read_only=True)

    class Meta:
        model = AdmissionTicket
        fields = '__all__'