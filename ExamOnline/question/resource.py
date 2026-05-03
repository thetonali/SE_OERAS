from import_export import resources, fields
from question.models import Choice, Fill, Judge, Subjective


class ChoiceResource(resources.ModelResource):
    # ===== 加入 subject =====
    subject = fields.Field(attribute='subject', column_name='科目')
    question = fields.Field(attribute='question', column_name='题目')
    answer_A = fields.Field(attribute='answer_A', column_name='A选项')
    answer_B = fields.Field(attribute='answer_B', column_name='B选项')
    answer_C = fields.Field(attribute='answer_C', column_name='C选项')
    answer_D = fields.Field(attribute='answer_D', column_name='D选项')
    right_answer = fields.Field(attribute='right_answer', column_name='正确答案')
    analysis = fields.Field(attribute='analysis', column_name='解析')
    score = fields.Field(attribute='score', column_name='分值')
    level = fields.Field(attribute='level', column_name='难度')

    class Meta:
        model = Choice
        fields = ('subject', 'question', 'answer_A', 'answer_B', 'answer_C',
                  'answer_D', 'right_answer', 'analysis', 'score', 'level')
        import_id_fields = []
        skip_unchanged = True


class FillResource(resources.ModelResource):
    subject = fields.Field(attribute='subject', column_name='科目')
    question = fields.Field(attribute='question', column_name='题目')
    right_answer = fields.Field(attribute='right_answer', column_name='正确答案')
    analysis = fields.Field(attribute='analysis', column_name='解析')
    score = fields.Field(attribute='score', column_name='分值')
    level = fields.Field(attribute='level', column_name='难度')

    class Meta:
        model = Fill
        fields = ('subject', 'question', 'right_answer', 'analysis', 'score', 'level')
        import_id_fields = []
        skip_unchanged = True


class JudgeResource(resources.ModelResource):
    subject = fields.Field(attribute='subject', column_name='科目')
    question = fields.Field(attribute='question', column_name='题目')
    right_answer = fields.Field(attribute='right_answer', column_name='正确答案(T/F)')
    analysis = fields.Field(attribute='analysis', column_name='解析')
    score = fields.Field(attribute='score', column_name='分值')
    level = fields.Field(attribute='level', column_name='难度')

    class Meta:
        model = Judge
        fields = ('subject', 'question', 'right_answer', 'analysis', 'score', 'level')
        import_id_fields = []
        skip_unchanged = True


class SubjectiveResource(resources.ModelResource):
    subject = fields.Field(attribute='subject', column_name='科目')
    question = fields.Field(attribute='question', column_name='题目')
    answer_template = fields.Field(attribute='answer_template', column_name='答题模板')
    analysis = fields.Field(attribute='analysis', column_name='解析')
    score = fields.Field(attribute='score', column_name='分值')
    level = fields.Field(attribute='level', column_name='难度')

    class Meta:
        model = Subjective
        fields = ('subject', 'question', 'answer_template', 'analysis', 'score', 'level')
        import_id_fields = []
        skip_unchanged = True