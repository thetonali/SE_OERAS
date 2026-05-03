import xadmin
from exam.models import Exam, Grade, Paper, SubjectiveAnswer
from xadmin.views import CommAdminView, BaseAdminView


class GlobalSetting(object):
    # ===== 修改标题 =====
    site_title = 'OERAS 在线考试管理系统'
    site_footer = '在线考试报名与考试管理系统'


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class ExamAdmin(object):
    # ===== 加入 category，去掉原来的 major（保留 major 显示但不强调）=====
    list_display = ['id', 'name', 'category', 'major', 'exam_date', 'total_time', 'paper', 'tips', 'clazzs']
    list_filter = ['category', 'major', 'exam_date']
    search_fields = ['id', 'name', 'major']
    list_display_links = ['name']
    list_per_page = 10
    model_icon = 'fa fa-book'
    relfield_style = 'fk-ajax'
    filter_horizontal = ('clazzs',)
    style_fields = {'clazzs': 'm2m_transfer'}


class PaperAdmin(object):
    # ===== 加入 subject =====
    list_display = ['id', 'name', 'subject', 'score', 'choice_number', 'fill_number',
                    'judge_number', 'subjective_number', 'level']
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
    list_display = ['id', 'student', 'exam', 'question', 'answer', 'score', 'create_time', 'update_time']
    list_filter = ['student', 'exam', 'score']
    list_editable = ['score']
    search_fields = ['student', 'exam', 'question']
    list_display_links = ['score']
    list_per_page = 20
    model_icon = 'fa fa-check-square-o'

    def has_add_permission(self):
        return False


xadmin.site.register(CommAdminView, GlobalSetting)
xadmin.site.register(BaseAdminView, BaseSetting)
xadmin.site.register(Exam, ExamAdmin)
xadmin.site.register(Paper, PaperAdmin)
xadmin.site.register(Grade, GradeAdmin)
xadmin.site.register(SubjectiveAnswer, SubjectiveAnswerAdmin)