import logging
from datetime import datetime, time, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.utils import OperationalError
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import escape
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from openpyxl import Workbook

from exam.filter import ExamFilter
from exam.models import Exam, Grade, Practice, SubjectiveAnswer, ExamRegistration, SubjectiveReviewHistory
from exam.serializers import ExamSerializer, GradeSerializer, PracticeSerializer, SubjectiveSerializer, \
    ExamRegistrationSerializer
from exam.services import suggest_subjective_score
from user.models import Student


logger = logging.getLogger(__name__)


def exam_start_at(exam):
    start_time = exam.start_time or time(9, 0)
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time[:5], "%H:%M").time()
    return datetime.combine(exam.exam_date, start_time)


def exam_end_at(exam):
    start_at = exam_start_at(exam)
    end_time = getattr(exam, 'end_time', None)
    if end_time:
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time[:5], "%H:%M").time()
        end_at = datetime.combine(exam.exam_date, end_time)
        if end_at <= start_at:
            end_at += timedelta(days=1)
        return end_at
    return start_at + timedelta(minutes=exam.total_time or 0)


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

        now = datetime.now()
        try:
            registered_exam_ids = set(
                ExamRegistration.objects.filter(student_id=student_id).values_list('exam_id', flat=True)
            )
        except OperationalError:
            registered_exam_ids = set()

        visible_ids = []
        for exam in self.queryset:
            if now > exam_end_at(exam):
                continue
            if exam.id in registered_exam_ids or now < exam_start_at(exam):
                visible_ids.append(exam.id)

        self.queryset = self.queryset.filter(id__in=visible_ids)
        return self.queryset

    @action(detail=True, methods=['get'], url_path='export-students')
    def export_students(self, request, pk=None):
        exam = self.get_object()
        try:
            registrations = list(ExamRegistration.objects.filter(exam=exam).select_related(
                'student', 'student__user', 'student__clazz'
            ).order_by('id'))
        except OperationalError:
            registrations = None

        wb = Workbook()
        ws = wb.active
        ws.title = 'students'
        ws.append([
            'Admission Number', 'Student ID', 'Username', 'Name', 'Gender', 'Class',
            'Exam', 'Exam Date', 'Start Time', 'End Time', 'Register Time', 'Score', 'Status'
        ])

        if registrations is None:
            if exam.clazzs.exists():
                students = Student.objects.filter(clazz__in=exam.clazzs.all()).distinct().order_by('id')
            else:
                students = Student.objects.all().order_by('id')
        else:
            students = [registration.student for registration in registrations]

        registration_map = {}
        if registrations is not None:
            registration_map = {registration.student_id: registration for registration in registrations}

        for student in students:
            registration = registration_map.get(student.id)
            grade = Grade.objects.filter(exam=exam, student=student).order_by('-create_time').first()
            clazz = student.clazz
            clazz_name = '{}{}{}'.format(clazz.year, clazz.major, clazz.clazz) if clazz else ''
            ws.append([
                registration.admission_number if registration else '',
                student.id,
                student.user.username if student.user else '',
                student.name,
                student.gender,
                clazz_name,
                exam.name,
                str(exam.exam_date),
                exam.start_time.strftime('%H:%M') if exam.start_time else '',
                exam.end_time.strftime('%H:%M') if exam.end_time else '',
                registration.create_time.strftime('%Y-%m-%d %H:%M:%S') if registration else '',
                grade.score if grade else '',
                'Submitted' if grade else ('Migration pending' if registrations is None else 'Registered'),
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="exam_students_{}.xlsx"'.format(exam.id)
        wb.save(response)
        return response


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


class ExamRegistrationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ExamRegistration.objects.all().order_by('-create_time')
    serializer_class = ExamRegistrationSerializer
    pagination_class = CommonPagination

    def get_queryset(self):
        queryset = ExamRegistration.objects.select_related('exam', 'exam__paper', 'student').all()
        student_id = self.request.query_params.get('student_id')
        exam_id = self.request.query_params.get('exam_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        return queryset.order_by('-create_time')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except OperationalError:
            return Response(
                {'msg': '报名表尚未创建，请先执行 python manage.py migrate'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    def create(self, request, *args, **kwargs):
        exam_id = request.data.get('exam_id')
        student_id = request.data.get('student_id')
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'msg': '考试不存在'}, status=status.HTTP_404_NOT_FOUND)

        if datetime.now() >= exam_start_at(exam):
            return Response({'msg': '考试已经开始，不能再报名'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            registration, created = ExamRegistration.objects.get_or_create(
                exam_id=exam_id,
                student_id=student_id,
            )
        except OperationalError:
            return Response(
                {'msg': '报名表尚未创建，请先执行 python manage.py migrate'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        serializer = self.get_serializer(registration)
        status_code = 201 if created else 200
        return Response(serializer.data, status=status_code)


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


class AIScoreAPIView(APIView):
    def get(self, request):
        answer_id = request.query_params.get('answer_id')
        return self._suggest(answer_id)

    def post(self, request):
        answer_id = request.data.get('answer_id')
        return self._suggest(answer_id)

    def _suggest(self, answer_id):
        if not answer_id:
            return Response({'message': 'answer_id is required'}, status=400)

        try:
            item = SubjectiveAnswer.objects.select_related('question').get(id=answer_id)
        except SubjectiveAnswer.DoesNotExist:
            return Response({'message': 'answer not found'}, status=404)

        suggestion = suggest_subjective_score(item.answer, item.question)

        return Response({
            'message': 'success',
            'answer_id': item.id,
            'question_id': item.question_id,
            'score_min': suggestion['score_min'],
            'score_max': suggestion['score_max'],
            'max_score': item.question.score,
            'reason': suggestion['reason'],
        })


def _review_queryset(user):
    if not user.is_authenticated:
        return SubjectiveAnswer.objects.none()
    return SubjectiveAnswer.objects.select_related('exam', 'question').all()


def review_tasks_view(request):
    if not request.user.is_authenticated:
        return redirect('/xadmin/')

    tasks = _review_queryset(request.user).order_by(F('score').asc(nulls_first=True), 'id')
    rows = []
    for task in tasks:
        standard = task.question.analysis or task.question.answer_template or '暂无评分标准'
        rows.append(
            '<tr>'
            f'<td>{escape(task.anonymous_code)}</td>'
            f'<td>{escape(task.exam.name)}</td>'
            f'<td>{escape(task.question.question)}</td>'
            f'<td>{task.question.score}</td>'
            f'<td>{escape(standard)}</td>'
            f'<td>{escape(task.review_status)}</td>'
            f'<td><a class="button" href="/review/tasks/{task.id}/">开始批改</a></td>'
            '</tr>'
        )

    html = f"""
    <!doctype html>
    <html lang="zh-CN">
    <head>
      <meta charset="utf-8">
      <title>AI协同阅卷任务</title>
      <style>
        body {{ margin: 0; background: #f5f7fb; color: #1f2d3d; font-family: Arial, "Microsoft YaHei", sans-serif; }}
        header {{ background: #1a3a6e; color: #fff; padding: 20px 36px; }}
        main {{ padding: 28px 36px; }}
        table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e4e7ed; }}
        th, td {{ border-bottom: 1px solid #ebeef5; padding: 12px; text-align: left; vertical-align: top; }}
        th {{ background: #eef5ff; }}
        .button {{ color: #fff; background: #2563eb; padding: 6px 12px; border-radius: 4px; text-decoration: none; }}
        .hint {{ color: #606266; margin-top: 8px; }}
      </style>
    </head>
    <body>
      <header>
        <h1>AI协同阅卷任务</h1>
        <div class="hint">任务列表已匿名处理，不展示考生姓名、准考证号等身份信息。</div>
      </header>
      <main>
        <table>
          <thead>
            <tr>
              <th>匿名编号</th><th>考试</th><th>题目内容</th><th>满分</th><th>评分标准</th><th>状态</th><th>操作</th>
            </tr>
          </thead>
          <tbody>{''.join(rows) if rows else '<tr><td colspan="7">暂无阅卷任务</td></tr>'}</tbody>
        </table>
      </main>
    </body>
    </html>
    """
    return HttpResponse(html)


def review_task_detail_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('/xadmin/')

    task = get_object_or_404(_review_queryset(request.user), pk=pk)
    max_score = task.question.score
    error = ''
    latest_history = task.histories.first()
    latest_comment = latest_history.new_comment if latest_history else ''

    if request.method == 'POST':
        raw_score = request.POST.get('score', '').strip()
        comment = request.POST.get('comment', '').strip()
        try:
            score = int(raw_score)
            if score < 0 or score > max_score:
                raise ValueError()

            old_score = task.score
            old_comment = latest_comment
            task.score = score
            task.full_clean()
            task.save(update_fields=['score', 'update_time'])
            SubjectiveReviewHistory.objects.create(
                subjective_answer=task,
                operator=request.user.username,
                old_score=old_score,
                new_score=score,
                old_comment=old_comment,
                new_comment=comment,
            )
            latest_comment = comment
            return redirect(f'/review/tasks/{task.id}/')
        except ValueError:
            error = f'最终得分必须是 0 到 {max_score} 之间的整数。'

    histories = ''.join(
        f'<li>{escape(history.create_time.strftime("%Y-%m-%d %H:%M:%S"))} '
        f'{escape(history.operator)}：{history.old_score if history.old_score is not None else "未阅"} '
        f'→ {history.new_score}</li>'
        for history in task.histories.all()[:20]
    )
    csrf_token = get_token(request)
    standard = task.question.analysis or task.question.answer_template or '暂无评分标准'

    html = f"""
    <!doctype html>
    <html lang="zh-CN">
    <head>
      <meta charset="utf-8">
      <title>匿名阅卷 - {escape(task.anonymous_code)}</title>
      <style>
        body {{ margin: 0; background: #f5f7fb; color: #1f2d3d; font-family: Arial, "Microsoft YaHei", sans-serif; }}
        header {{ background: #1a3a6e; color: #fff; padding: 18px 34px; }}
        main {{ display: grid; grid-template-columns: 1fr 340px; gap: 22px; padding: 28px 34px; }}
        section {{ background: #fff; border: 1px solid #e4e7ed; border-radius: 6px; padding: 22px; }}
        .muted {{ color: #606266; }}
        .answer {{ white-space: pre-wrap; line-height: 1.8; background: #f8fafc; padding: 14px; border: 1px solid #ebeef5; }}
        .ai {{ border-left: 4px solid #2563eb; background: #eef5ff; }}
        .ai.hidden {{ display: none; }}
        input, textarea {{ width: 100%; box-sizing: border-box; padding: 8px; border: 1px solid #dcdfe6; border-radius: 4px; }}
        textarea {{ min-height: 120px; }}
        button {{ background: #2563eb; color: #fff; border: 0; padding: 9px 16px; border-radius: 4px; cursor: pointer; }}
        .error {{ color: #f56c6c; }}
        a {{ color: #2563eb; }}
      </style>
    </head>
    <body>
      <header>
        <a href="/review/tasks/" style="color:#fff;">返回任务列表</a>
        <h1>匿名阅卷：{escape(task.anonymous_code)}</h1>
        <div>状态：{escape(task.review_status)}，满分：{max_score} 分</div>
      </header>
      <main>
        <div>
          <section>
            <h2>题目内容</h2>
            <p>{escape(task.question.question)}</p>
            <h3>评分标准</h3>
            <p class="muted">{escape(standard)}</p>
            <h3>考生答案</h3>
            <div class="answer">{escape(task.answer or "未作答")}</div>
          </section>
        </div>
        <div>
          <section id="aiBox" class="ai">
            <h2>AI建议</h2>
            <p id="aiLoading">正在生成建议...</p>
            <div id="aiResult" style="display:none;">
              <p><b>建议分数区间：</b><span id="aiRange"></span></p>
              <p><b>评分依据：</b><span id="aiReason"></span></p>
            </div>
          </section>
          <section style="margin-top:18px;">
            <h2>教师评分</h2>
            <form method="post">
              <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
              <p class="error">{escape(error)}</p>
              <label>最终得分（0 - {max_score}）</label>
              <input name="score" type="number" min="0" max="{max_score}" value="{task.score if task.score is not None else ''}" required>
              <label>文字评语</label>
              <textarea name="comment">{escape(latest_comment)}</textarea>
              <p><button type="submit">保存评分</button></p>
            </form>
          </section>
          <section style="margin-top:18px;">
            <h2>分数变更历史</h2>
            <ul>{histories if histories else '<li>暂无变更记录</li>'}</ul>
          </section>
        </div>
      </main>
      <script>
        fetch('/api/review/tasks/{task.id}/ai-suggestion/')
          .then(function(response) {{
            if (!response.ok) throw new Error('AI unavailable');
            return response.json();
          }})
          .then(function(data) {{
            document.getElementById('aiLoading').style.display = 'none';
            document.getElementById('aiResult').style.display = 'block';
            document.getElementById('aiRange').innerText = data.score_min + '～' + data.score_max + ' / ' + data.max_score + ' 分';
            document.getElementById('aiReason').innerText = data.reason;
          }})
          .catch(function() {{
            document.getElementById('aiBox').className = 'ai hidden';
          }});
      </script>
    </body>
    </html>
    """
    return HttpResponse(html)


def review_task_ai_suggestion_view(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'unauthorized'}, status=401)

    task = get_object_or_404(_review_queryset(request.user), pk=pk)
    try:
        suggestion = suggest_subjective_score(task.answer, task.question)
        return JsonResponse({
            'score_min': suggestion['score_min'],
            'score_max': suggestion['score_max'],
            'max_score': task.question.score,
            'reason': suggestion['reason'],
        })
    except Exception as exc:
        logger.exception('AI suggestion failed for subjective answer %s', pk)
        return JsonResponse({'message': 'AI unavailable'}, status=503)
