from django.contrib.auth.models import User
from django.test import TestCase

from exam.models import Practice
from question.models import Choice, Fill, Judge, Subjective
from record.models import ChoiceRecord, FillRecord, JudgeRecord, SubjectiveRecord
from user.models import Clazz, Student


class RecordModelTest(TestCase):
    def setUp(self):
        clazz = Clazz.objects.create(year="2026", major="SE", clazz="3")
        user = User.objects.create_user(username="record001", password="pass123456")
        self.student = Student.objects.create(name="RecordStudent", user=user, gender="m", clazz=clazz)
        self.practice = Practice.objects.create(name="manual-name", student=self.student)

    def test_practice_name_is_generated_on_save(self):
        self.assertRegex(self.practice.name, r"^模拟练习\d{8}\d{4}$")

    def test_choice_fill_judge_and_subjective_records_are_saved(self):
        choice = Choice.objects.create(
            subject="SE",
            question="Choice",
            answer_A="A",
            answer_B="B",
            answer_C="C",
            answer_D="D",
            right_answer="A",
        )
        fill = Fill.objects.create(subject="SE", question="Fill", right_answer="answer")
        judge = Judge.objects.create(subject="SE", question="Judge", right_answer="T")
        subjective = Subjective.objects.create(subject="SE", question="Subjective")

        ChoiceRecord.objects.create(
            practice=self.practice,
            student=self.student,
            choice=choice,
            your_answer="A",
        )
        FillRecord.objects.create(
            practice=self.practice,
            student=self.student,
            fill=fill,
            your_answer="answer",
        )
        JudgeRecord.objects.create(
            practice=self.practice,
            student=self.student,
            judge=judge,
            your_answer="T",
        )
        SubjectiveRecord.objects.create(
            practice=self.practice,
            student=self.student,
            program=subjective,
            your_answer="essay answer",
            cmd_msg="accepted",
        )

        self.assertEqual(ChoiceRecord.objects.count(), 1)
        self.assertEqual(FillRecord.objects.count(), 1)
        self.assertEqual(JudgeRecord.objects.count(), 1)
        self.assertEqual(SubjectiveRecord.objects.count(), 1)
