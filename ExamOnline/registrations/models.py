from django.db import models
from user.models import Student
from exam.models import Exam

class Registration(models.Model):
    """报名记录模型"""
    STATUS_CHOICES = (
        ('0', '待审核'),
        ('1', '已通过'),
        ('2', '已拒绝')
    )
    student = models.ForeignKey(Student, verbose_name="学生", on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, verbose_name="考试", on_delete=models.CASCADE)
    status = models.CharField("状态", max_length=1, choices=STATUS_CHOICES, default='0')
    apply_time = models.DateTimeField("申请时间", auto_now_add=True)
    review_time = models.DateTimeField("审核时间", null=True, blank=True)

    class Meta:
        ordering = ['-apply_time']
        verbose_name = "报名记录"
        verbose_name_plural = verbose_name
        # 确保同一个学生对同一场考试只能报名一次
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.name} - {self.exam.name} - {self.get_status_display()}"


class AdmissionTicket(models.Model):
    """准考证模型"""
    registration = models.OneToOneField(Registration, verbose_name="报名记录", on_delete=models.CASCADE)
    ticket_number = models.CharField("准考证号", max_length=20, unique=True)
    pdf_file = models.FileField("准考证PDF文件", upload_to='tickets/', null=True, blank=True)
    generate_time = models.DateTimeField("生成时间", auto_now_add=True)

    class Meta:
        ordering = ['-generate_time']
        verbose_name = "准考证"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.registration.student.name} - {self.ticket_number}"