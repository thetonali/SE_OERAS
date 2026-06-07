from django.core.exceptions import ValidationError
from django.db import models
from question.models import Choice, Fill, Judge, Subjective
from user.models import Student, Clazz
from datetime import datetime, timedelta
import random
import string


class Paper(models.Model):
    """试卷模型类"""
    LEVEL_CHOICES = (
        ('1', '入门'), ('2', '简单'), ('3', '普通'), ('4', '较难'), ('5', '困难')
    )
    name = models.CharField("试卷名称", max_length=50, default="")
    # ===== 新增：科目，用于从题库按科目抽题 =====
    subject = models.CharField("科目", max_length=50, default="通用",
                               help_text="填写与题目科目一致的名称，抽题时按此科目过滤")
    score = models.PositiveSmallIntegerField("总分", default=100)
    choice_number = models.PositiveSmallIntegerField("选择题数", default=10)
    fill_number = models.PositiveSmallIntegerField("填空题数", default=10)
    judge_number = models.PositiveSmallIntegerField("判断题数", default=10)
    subjective_number = models.PositiveSmallIntegerField("主观题数", default=5)
    level = models.CharField("难度等级", max_length=1, choices=LEVEL_CHOICES, default="1")

    class Meta:
        ordering = ["id"]
        verbose_name = "试卷"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.score = (self.choice_number + self.fill_number + self.judge_number) * 2 + self.subjective_number * 8
        super().save(*args, **kwargs)


class Exam(models.Model):
    """考试模型类"""
    # ===== 新增：考试类别，替代原来写死的 major =====
    CATEGORY_CHOICES = (
        ('qualification', '资质认证'),
        ('course', '课程考试'),
        ('competition', '竞赛选拔'),
        ('other', '其他'),
    )
    name = models.CharField("考试名称", max_length=50, default="")
    # ===== 新增 category，保留 major 但设为可空（不删，避免迁移出错）=====
    category = models.CharField("考试类别", max_length=20, choices=CATEGORY_CHOICES,
                                default='other', null=True, blank=True)
    major = models.CharField("专业方向", max_length=50, default="",
                             help_text="可填写适用专业，留空表示不限专业")
    exam_date = models.DateField("考试日期", default="")
    start_time = models.TimeField("开始时间", default="09:00")
    end_time = models.TimeField("结束时间", default="11:00")
    total_time = models.PositiveSmallIntegerField("时长(分钟)", default=120)
    paper = models.OneToOneField(Paper, on_delete=models.CASCADE, verbose_name="试卷", default="")
    tips = models.TextField("考生须知", default="")
    # ===== 保留 clazzs，设为可选（不限班级的考试留空即可）=====
    clazzs = models.ManyToManyField(Clazz, verbose_name="限定班级", blank=True,
                                    help_text="留空表示所有学生均可报名；选择班级则仅限该班级学生")

    class Meta:
        ordering = ["id"]
        db_table = 'exam_info'
        verbose_name = "考试"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_time and self.end_time and self.start_time == self.end_time:
            raise ValidationError({'end_time': '考试结束时间不能等于开始时间。'})

    def save(self, *args, **kwargs):
        if self.exam_date and self.start_time and self.end_time:
            exam_date = self.exam_date
            start_time = self.start_time
            end_time = self.end_time
            if isinstance(exam_date, str):
                exam_date = datetime.strptime(exam_date, "%Y-%m-%d").date()
            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time[:5], "%H:%M").time()
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time[:5], "%H:%M").time()

            start_at = datetime.combine(exam_date, start_time)
            end_at = datetime.combine(exam_date, end_time)
            if end_at <= start_at:
                end_at += timedelta(days=1)
            self.total_time = int((end_at - start_at).total_seconds() // 60)
        super().save(*args, **kwargs)


class Grade(models.Model):
    """成绩模型类"""
    exam = models.ForeignKey(Exam, verbose_name="考试", on_delete=models.CASCADE)
    student = models.ForeignKey(Student, verbose_name="学生", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField("分数", default=0)
    create_time = models.DateTimeField("创建日期", auto_now_add=True)
    update_time = models.DateTimeField("修改日期", auto_now=True)
    identifier = models.CharField("标识符", max_length=8, default="")

    class Meta:
        ordering = ['id']
        verbose_name = '成绩'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.student}的{self.exam}成绩为{self.score}分'


class Practice(models.Model):
    """模拟练习"""
    name = models.CharField("练习名称", max_length=20)
    student = models.ForeignKey(Student, verbose_name="学生", on_delete=models.CASCADE)
    create_time = models.DateTimeField("练习时间", auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = '练习'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = f'模拟练习{datetime.now().strftime("%Y%m%d")}{random.randint(1000, 9999)}'
        super().save(*args, **kwargs)


class SubjectiveAnswer(models.Model):
    """主观题批改"""
    student = models.ForeignKey(Student, verbose_name="学生", on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, verbose_name="考试", on_delete=models.CASCADE)
    question = models.ForeignKey(Subjective, verbose_name="题目", on_delete=models.CASCADE)
    answer = models.TextField("答案", default="")
    score = models.PositiveSmallIntegerField("分数", null=True, blank=True)
    create_time = models.DateTimeField("创建日期", auto_now_add=True)
    update_time = models.DateTimeField("修改日期", auto_now=True)
    identifier = models.CharField("标识符", max_length=8, default="")

    class Meta:
        ordering = ['id']
        verbose_name = '主观题批改'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.student}的{self.question}得{self.score}分'

    def clean(self):
        if self.score is not None and self.question_id:
            if self.score < 0 or self.score > self.question.score:
                raise ValidationError({'score': '最终得分必须在 0 到题目满分之间。'})

    @property
    def review_status(self):
        return '已阅' if self.score is not None else '未阅'

    @property
    def anonymous_code(self):
        return f"ANSWER-{self.id:06d}"


def generate_admission_number(exam_id, student_id):
    suffix = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    date_part = datetime.now().strftime("%Y%m%d")
    return f"OERAS-{date_part}-{exam_id:04d}-{student_id:04d}-{suffix}"


class ExamRegistration(models.Model):
    """考试报名记录"""
    exam = models.ForeignKey(Exam, verbose_name="考试", on_delete=models.CASCADE)
    student = models.ForeignKey(Student, verbose_name="学生", on_delete=models.CASCADE)
    admission_number = models.CharField("准考证号", max_length=32, unique=True, blank=True)
    create_time = models.DateTimeField("报名时间", auto_now_add=True)

    class Meta:
        ordering = ['-create_time']
        unique_together = ('exam', 'student')
        verbose_name = '考试报名'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.student}-{self.exam}'

    def save(self, *args, **kwargs):
        if not self.admission_number and self.exam_id and self.student_id:
            self.admission_number = generate_admission_number(self.exam_id, self.student_id)
        super().save(*args, **kwargs)


class SubjectiveReviewHistory(models.Model):
    """主观题分数变更历史"""
    subjective_answer = models.ForeignKey(
        SubjectiveAnswer, verbose_name="主观题答案",
        on_delete=models.CASCADE, related_name="histories"
    )
    operator = models.CharField("操作人", max_length=50, default="")
    old_score = models.PositiveSmallIntegerField("变更前分值", null=True, blank=True)
    new_score = models.PositiveSmallIntegerField("变更后分值", null=True, blank=True)
    old_comment = models.TextField("变更前评语", default="", blank=True)
    new_comment = models.TextField("变更后评语", default="", blank=True)
    create_time = models.DateTimeField("操作时间", auto_now_add=True)

    class Meta:
        ordering = ['-create_time']
        verbose_name = '主观题评分历史'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.subjective_answer_id}: {self.old_score}->{self.new_score}'
