from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from exam.models import SubjectiveAnswer
from question.models import Choice, Fill, Judge, Subjective
from question.serializers import (
    ChoiceSerializer,
    FillSerializer,
    JudgeSerializer,
    SubjectiveSerializer
)


# =========================
# 工具函数（防空 & 统一处理）
# =========================
def safe_level(level):
    return str(level) if level is not None else "1"


def filter_by_subject(queryset, subject):
    """
    模糊匹配 subject，避免“空格/中文差异导致查不到”
    """
    if subject:
        return queryset.filter(subject__icontains=subject)
    return queryset


# =========================
# 选择题
# =========================
class ChoiceListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Choice.objects.none()
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        choice_number = int(self.request.query_params.get("choice_number") or 0)
        level = safe_level(self.request.query_params.get("level"))
        subject = self.request.query_params.get("subject")

        if not choice_number:
            return Choice.objects.none()

        qs = Choice.objects.filter(level=level)
        qs = filter_by_subject(qs, subject)

        return qs.order_by('?')[:choice_number]


# =========================
# 填空题
# =========================
class FillListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Fill.objects.none()
    serializer_class = FillSerializer

    def get_queryset(self):
        fill_number = int(self.request.query_params.get("fill_number") or 0)
        level = safe_level(self.request.query_params.get("level"))
        subject = self.request.query_params.get("subject")

        if not fill_number:
            return Fill.objects.none()

        qs = Fill.objects.filter(level=level)
        qs = filter_by_subject(qs, subject)

        return qs.order_by('?')[:fill_number]


# =========================
# 判断题
# =========================
class JudgeListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Judge.objects.none()
    serializer_class = JudgeSerializer

    def get_queryset(self):
        judge_number = int(self.request.query_params.get("judge_number") or 0)
        level = safe_level(self.request.query_params.get("level"))
        subject = self.request.query_params.get("subject")

        if not judge_number:
            return Judge.objects.none()

        qs = Judge.objects.filter(level=level)
        qs = filter_by_subject(qs, subject)

        return qs.order_by('?')[:judge_number]


# =========================
# 主观题
# =========================
class SubjectiveListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Subjective.objects.none()
    serializer_class = SubjectiveSerializer

    def get_queryset(self):
        subjective_number = int(self.request.query_params.get("subjective_number") or 0)
        level = safe_level(self.request.query_params.get("level"))
        subject = self.request.query_params.get("subject")

        if not subjective_number:
            return Subjective.objects.none()

        qs = Subjective.objects.filter(level=level)
        qs = filter_by_subject(qs, subject)

        return qs.order_by('?')[:subjective_number]


# =========================
# 上传主观题答案
# =========================
class UploadSubjective(APIView):

    def post(self, request):
        data = request.data

        SubjectiveAnswer.objects.create(
            student_id=data.get("student_id"),
            question_id=data.get("question_id"),
            answer=data.get("answer"),
            exam_id=data.get("exam_id"),
            identifier=data.get("identifier"),
        )

        return Response({"message": "success"})


# =========================
# ⭐ 核心：统一组卷接口（最终稳定版）
# =========================
class GeneratePaperAPIView(APIView):

    def get(self, request):
       paper_id = request.query_params.get("paper_id")
       
       if not paper_id:
           return Response({"error": "paper_id不能为空"}, status=400)
       
       # 从数据库读取试卷配置
       try:
           from exam.models import Paper
           paper = Paper.objects.get(id=paper_id)
       except Paper.DoesNotExist:
            return Response({"error": "试卷不存在"}, status=404)

       subject = paper.subject
       level = str(paper.level)

       if not subject:
           return Response({"error": "试卷未配置科目"}, status=400)

        # 先检查是否有数据（防空卷）
       if not Choice.objects.filter(subject__icontains=subject, level=level).exists():
            return Response({
                "error": "题库中没有匹配数据",
                "subject": subject,
                "level": level
            }, status=400)
            
       result = {
            "choice": ChoiceSerializer(
                filter_by_subject(Choice.objects.filter(level=level), subject)
                .order_by('?')[:paper.choice_number],
                many=True
            ).data,

            "fill": FillSerializer(
                filter_by_subject(Fill.objects.filter(level=level), subject)
                .order_by('?')[:paper.fill_number],
                many=True
            ).data,

            "judge": JudgeSerializer(
                filter_by_subject(Judge.objects.filter(level=level), subject)
                .order_by('?')[:paper.judge_number],
                many=True
            ).data,

            "subjective": SubjectiveSerializer(
                filter_by_subject(Subjective.objects.filter(level=level), subject)
                .order_by('?')[:paper.subjective_number],
                many=True
            ).data,
        }
       
       return Response(result)