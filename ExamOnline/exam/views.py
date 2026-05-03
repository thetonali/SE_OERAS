from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.pagination import PageNumberPagination

from exam.filter import ExamFilter
from exam.models import Exam, Grade, Practice, SubjectiveAnswer
from exam.serializers import ExamSerializer, GradeSerializer, PracticeSerializer, SubjectiveSerializer
from user.models import Student


class CommonPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 10


class ExamListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """考试列表页"""
    queryset = Exam.objects.all().order_by('id')
    serializer_class = ExamSerializer
    pagination_class = CommonPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = ExamFilter
    search_fields = ('name', 'major', 'category')
    ordering_fields = ('id', 'exam_date')

    def get_queryset(self):
        student_id = self.request.query_params.get("student_id")

        # ===== 核心修改：改为通用考试列表逻辑 =====
        # 如果考试没有限定班级（clazzs 为空），所有学生都能看到
        # 如果考试限定了班级，只有该班级学生能看到
        # 两类都显示给该学生

        if not student_id:
            # 没有传 student_id，返回全部（兼容管理员查看场景）
            return Exam.objects.all().order_by('id')

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Exam.objects.none()

        # 没有限定班级的考试（所有人可见） + 限定了该学生班级的考试
        from django.db.models import Q
        self.queryset = Exam.objects.filter(
            Q(clazzs__isnull=True) | Q(clazzs=student.clazz)
        ).distinct().order_by('id')

        return self.queryset


class GradeListViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """成绩列表"""
    queryset = Grade.objects.all().order_by('-create_time')
    serializer_class = GradeSerializer
    pagination_class = CommonPagination

    def get_queryset(self):
        student_id = self.request.query_params.get("student_id")
        if student_id:
            self.queryset = Grade.objects.filter(student_id=student_id)
        for grade in self.queryset:
            subjective_list = SubjectiveAnswer.objects.filter(
                student_id=student_id, exam_id=grade.exam_id, identifier=grade.identifier
            )
            if subjective_list:
                score = grade.score
                for subjective in subjective_list:
                    score += subjective.score if subjective.score else 0
                grade.score = score
        return self.queryset


class PracticeListViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """练习列表"""
    queryset = Practice.objects.all()
    serializer_class = PracticeSerializer
    pagination_class = CommonPagination

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        if student_id:
            self.queryset = Practice.objects.filter(student_id=student_id)
        return self.queryset


class SubjectiveListViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """主观题列表"""
    queryset = SubjectiveAnswer.objects.filter()
    serializer_class = SubjectiveSerializer
    pagination_class = CommonPagination

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id')
        if student_id:
            self.queryset = SubjectiveAnswer.objects.filter(student_id=student_id)
        self.queryset = self.queryset.order_by(F('score').asc(nulls_first=True))
        return self.queryset