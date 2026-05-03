# ExamOnline/registrations/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Registration, AdmissionTicket
from .serializers import RegistrationSerializer, AdmissionTicketSerializer
from .utils import generate_ticket_pdf, generate_ticket_number
from user.models import Student


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    # 恢复原生的身份验证控制，跨域预检交由中间件处理
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 普通学生只能看自己的报名记录
        if hasattr(user, 'student'):
            return self.queryset.filter(student=user.student)
        return self.queryset

    def perform_create(self, serializer):
        student = self.request.user.student
        serializer.save(student=student)

    @action(detail=True, methods=['post'], url_path='audit')
    def audit_registration(self, request, pk=None):
        """管理员审核接口"""
        if not request.user.is_staff:
            return Response({"detail": "无权限执行此操作"}, status=status.HTTP_403_FORBIDDEN)
            
        registration = self.get_object()
        audit_status = request.data.get('status')
        
        if audit_status not in ['1', '2']:
            return Response({"detail": "状态参数错误"}, status=status.HTTP_400_BAD_REQUEST)
            
        registration.status = audit_status
        registration.review_time = timezone.now()
        registration.save()
        
        # 审核通过，自动生成准考证
        if audit_status == '1':
            ticket_number = generate_ticket_number()
            pdf_path = generate_ticket_pdf(
                student_name=registration.student.name,
                exam_name=registration.exam.name,
                exam_date=registration.exam.exam_date.strftime('%Y-%m-%d'),
                ticket_number=ticket_number
            )
            AdmissionTicket.objects.create(
                registration=registration,
                ticket_number=ticket_number,
                pdf_file=pdf_path
            )
            
        return Response({"detail": "审核完成"}, status=status.HTTP_200_OK)


class AdmissionTicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionTicket.objects.all()
    serializer_class = AdmissionTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student'):
            return self.queryset.filter(registration__student=user.student)
        return self.queryset