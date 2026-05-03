import xadmin

from question.models import Choice, Fill, Judge, Subjective
from question.resource import ChoiceResource, FillResource, JudgeResource, SubjectiveResource


class ChoiceAdmin(object):
    # ===== 加入 subject =====
    list_display = ['id', 'subject', 'question', 'answer_A', 'answer_B', 'answer_C', 'answer_D',
                    'right_answer', 'analysis', 'score', 'level']
    list_filter = ['subject', 'level']   # 可按科目和难度筛选
    search_fields = ['id', 'question', 'subject']
    list_display_links = ['question']
    list_per_page = 10
    model_icon = 'fa fa-question-circle-o'
    import_export_args = {'import_resource_class': ChoiceResource}


class FillAdmin(object):
    # ===== 加入 subject =====
    list_display = ['id', 'subject', 'question', 'right_answer', 'analysis', 'score', 'level']
    list_filter = ['subject', 'level']
    search_fields = ['id', 'question', 'subject']
    list_display_links = ['question']
    list_per_page = 10
    model_icon = 'fa fa-edit'
    import_export_args = {'import_resource_class': FillResource}


class JudgeAdmin(object):
    # ===== 加入 subject =====
    list_display = ['id', 'subject', 'question', 'right_answer', 'analysis', 'score', 'level']
    list_filter = ['subject', 'level']
    search_fields = ['id', 'question', 'subject']
    list_display_links = ['question']
    list_per_page = 10
    model_icon = 'fa fa-check-square-o'
    import_export_args = {'import_resource_class': JudgeResource}


class SubjectiveAdmin(object):
    # ===== 加入 subject =====
    list_display = ['id', 'subject', 'question', 'analysis', 'score', 'level']
    list_filter = ['subject', 'level']
    search_fields = ['id', 'question', 'subject']
    list_display_links = ['question']
    list_per_page = 10
    model_icon = 'fa fa-laptop'
    import_export_args = {'import_resource_class': SubjectiveResource}


xadmin.site.register(Choice, ChoiceAdmin)
xadmin.site.register(Fill, FillAdmin)
xadmin.site.register(Judge, JudgeAdmin)
xadmin.site.register(Subjective, SubjectiveAdmin)