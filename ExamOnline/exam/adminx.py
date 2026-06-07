import xadmin
from django.utils.html import format_html
from xadmin.views import BaseAdminView, CommAdminView

from exam.models import Exam, Grade, Paper, SubjectiveAnswer


class GlobalSetting(object):
    site_title = 'OERAS 在线考试管理系统'
    site_footer = '在线考试报名与考试管理系统'


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class ExamAdmin(object):
    list_display = [
        'id', 'name', 'category', 'major', 'exam_date', 'start_time', 'end_time', 'total_time',
        'paper', 'tips', 'clazzs', 'export_students_link'
    ]
    list_filter = ['category', 'major', 'exam_date', 'start_time', 'end_time']
    search_fields = ['id', 'name', 'major']
    list_display_links = ['name']
    list_per_page = 10
    model_icon = 'fa fa-book'
    relfield_style = 'fk-ajax'
    filter_horizontal = ('clazzs',)
    style_fields = {'clazzs': 'm2m_transfer'}

    def export_students_link(self, obj):
        return format_html(
            '<a class="btn btn-info btn-xs" href="/exams/{}/export-students/">导出考试名单</a>',
            obj.id
        )
    export_students_link.short_description = '考试名单'


class PaperAdmin(object):
    list_display = [
        'id', 'name', 'subject', 'score', 'choice_number', 'fill_number',
        'judge_number', 'subjective_number', 'level'
    ]
    list_filter = ['subject', 'level']
    search_fields = ['id', 'name', 'subject']
    list_display_links = ['name']
    list_per_page = 10
    model_icon = 'fa fa-file-text'


class GradeAdmin(object):
    list_display = ['id', 'exam', 'student', 'score', 'create_time', 'update_time']
    list_filter = ['exam', 'student', 'create_time']
    search_fields = ['exam', 'student']
    list_display_links = ['score']
    list_per_page = 10
    model_icon = 'fa fa-bar-chart'

    data_charts = {
        'grade_charts1': {
            'title': '考试成绩曲线图',
            'x-field': 'create_time',
            'y-field': ('score',),
            'order': ('id',)
        },
        'grade_charts2': {
            'title': '考试成绩柱状图',
            'x-field': 'score',
            'y-field': ('score',),
            'order': ('id',),
            'option': {
                "series": {"bars": {"align": "center", "barWidth": 0.5, "show": True}},
                "xaxis": {"aggregate": "count", "mode": "score"}
            }
        }
    }


class SubjectiveAnswerAdmin(object):
    list_display = [
        'id', 'anonymous_display', 'exam', 'question', 'max_score_display',
        'standard_display', 'review_status_display', 'review_task_link',
        'score', 'create_time', 'update_time'
    ]
    list_filter = ['exam', 'score']
    list_editable = ['score']
    search_fields = ['student', 'exam', 'question']
    list_display_links = ['id']
    list_per_page = 20
    model_icon = 'fa fa-check-square-o'

    def anonymous_display(self, obj):
        return obj.anonymous_code
    anonymous_display.short_description = '匿名编号'

    def max_score_display(self, obj):
        return obj.question.score
    max_score_display.short_description = '满分'

    def standard_display(self, obj):
        return obj.question.analysis or obj.question.answer_template or '暂无评分标准'
    standard_display.short_description = '评分标准'

    def review_status_display(self, obj):
        return obj.review_status
    review_status_display.short_description = '状态'

    def review_task_link(self, obj):
        return format_html(
            '<a class="btn btn-primary btn-xs" href="/review/tasks/{}/">匿名批改</a>',
            obj.id
        )
    review_task_link.short_description = '阅卷任务'

    def has_add_permission(self):
        return False


xadmin.site.register(CommAdminView, GlobalSetting)
xadmin.site.register(BaseAdminView, BaseSetting)
xadmin.site.register(Exam, ExamAdmin)
xadmin.site.register(Paper, PaperAdmin)
xadmin.site.register(Grade, GradeAdmin)
xadmin.site.register(SubjectiveAnswer, SubjectiveAnswerAdmin)
