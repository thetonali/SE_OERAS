# registrations/views.py
import uuid
import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Registration, AdmissionTicket
from .serializers import RegistrationSerializer
from .utils import generate_admission_ticket_pdf


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    报名记录视图集
    提供：报名申请、状态查询、管理员审核等功能
    """
    queryset = Registration.objects.all().order_by('-applied_at')
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 普通用户只能看到自己的报名记录，管理员可以看到所有
        user = self.request.user
        if user.is_staff:
            return Registration.objects.all().order_by('-applied_at')
        return Registration.objects.filter(user=user).order_by('-applied_at')

    def perform_create(self, serializer):
        # 创建报名申请时，自动绑定当前登录用户
        serializer.save(user=self.request.user, status='pending')

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def review(self, request, pk=None):
        """
        管理员审核接口
        请求参数：{"status": "approved" 或 "rejected", "remarks": "可选备注"}
        """
        registration = self.get_object()
        new_status = request.data.get('status')
        remarks = request.data.get('remarks', '')

        if new_status not in ['approved', 'rejected']:
            return Response({'error': '审核状态无效，必须为 approved 或 rejected'}, status=status.HTTP_400_BAD_REQUEST)

        # 更新状态
        registration.status = new_status
        registration.remarks = remarks
        registration.save()

        # 如果审核通过，自动生成准考证和PDF
        if new_status == 'approved':
            # 防止重复生成
            if not hasattr(registration, 'ticket'):
                # 生成唯一准考证号 (例如: 年月日+随机码)
                date_str = datetime.datetime.now().strftime('%Y%m%d')
                ticket_num = f"EXAM{date_str}{uuid.uuid4().hex[:6].upper()}"
                
                # 生成PDF文件
                pdf_path = generate_admission_ticket_pdf(
                    user_name=registration.user.username,
                    exam_name=registration.exam_name,
                    ticket_number=ticket_num
                )
                
                # 创建准考证记录
                AdmissionTicket.objects.create(
                    registration=registration,
                    ticket_number=ticket_num,
                    pdf_file_path=pdf_path
                )

        serializer = self.get_serializer(registration)
        return Response({'message': '审核完成', 'data': serializer.data}, status=status.HTTP_200_OK)
    