# registrations/models.py
from django.db import models
from django.contrib.auth.models import User

class Registration(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '已拒绝'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='考生')
    exam_name = models.CharField(max_length=255, verbose_name='考试名称')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    remarks = models.TextField(blank=True, null=True, verbose_name='管理员备注')

    class Meta:
        db_table = 'registration_record'
        verbose_name = '报名记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.exam_name} ({self.get_status_display()})"


class AdmissionTicket(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='ticket', verbose_name='报名记录')
    ticket_number = models.CharField(max_length=100, unique=True, verbose_name='准考证号')
    pdf_file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='PDF文件路径')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')

    class Meta:
        db_table = 'admission_ticket'
        verbose_name = '准考证'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"准考证: {self.ticket_number}"