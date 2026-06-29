from datetime import date, time

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from exam.models import (
    Exam,
    ExamRegistration,
    Paper,
    SubjectiveAnswer,
    SubjectiveReviewHistory,
)
from exam.views import exam_end_at, exam_start_at
from question.models import Subjective
from user.models import Clazz, Student


class ExamBusinessRuleTest(TestCase):
    def setUp(self):
        self.clazz = Clazz.objects.create(year="2026", major="SE", clazz="1")
        self.user = User.objects.create_user(username="student001", password="pass123456")
        self.student = Student.objects.create(
            name="Student001", user=self.user, gender="m", clazz=self.clazz
        )
        self.paper = Paper.objects.create(
            name="SE Paper",
            subject="Software Engineering",
            choice_number=3,
            fill_number=2,
            judge_number=1,
            subjective_number=2,
            level="2",
        )

    def test_paper_score_is_recalculated_from_question_counts(self):
        self.paper.choice_number = 5
        self.paper.fill_number = 4
        self.paper.judge_number = 3
        self.paper.subjective_number = 2
        self.paper.save()

        self.assertEqual(self.paper.score, (5 + 4 + 3) * 2 + 2 * 8)

    def test_exam_total_time_supports_cross_day_exam(self):
        exam = Exam.objects.create(
            name="Night Exam",
            paper=self.paper,
            exam_date=date(2026, 6, 28),
            start_time=time(23, 30),
            end_time=time(0, 30),
        )

        self.assertEqual(exam.total_time, 60)
        self.assertLess(exam_start_at(exam), exam_end_at(exam))

    def test_registration_generates_admission_number_and_prevents_duplicates(self):
        exam = Exam.objects.create(
            name="Registration Exam",
            paper=self.paper,
            exam_date=date(2099, 1, 1),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        registration = ExamRegistration.objects.create(exam=exam, student=self.student)

        self.assertRegex(
            registration.admission_number,
            r"^OERAS-\d{8}-\d{4}-\d{4}-[A-Z0-9]{4}$",
        )
        with self.assertRaises(IntegrityError):
            ExamRegistration.objects.create(exam=exam, student=self.student)


class SubjectiveReviewRuleTest(TestCase):
    def setUp(self):
        clazz = Clazz.objects.create(year="2026", major="SE", clazz="2")
        user = User.objects.create_user(username="review001", password="pass123456")
        self.student = Student.objects.create(name="ReviewStudent", user=user, gender="f", clazz=clazz)
        self.paper = Paper.objects.create(name="Review Paper", subject="SE")
        self.exam = Exam.objects.create(
            name="Review Exam",
            paper=self.paper,
            exam_date=date(2099, 1, 1),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        self.question = Subjective.objects.create(
            subject="SE",
            question="Describe black-box testing.",
            answer_template="Explain equivalence classes and boundary values.",
            analysis="Score by completeness and accuracy.",
            score=8,
            level="2",
        )

    def test_subjective_score_must_not_exceed_question_score(self):
        answer = SubjectiveAnswer(
            student=self.student,
            exam=self.exam,
            question=self.question,
            answer="Boundary value analysis checks edge inputs.",
            score=9,
            identifier="A0000001",
        )

        with self.assertRaises(ValidationError):
            answer.full_clean()

    def test_review_history_records_score_change(self):
        answer = SubjectiveAnswer.objects.create(
            student=self.student,
            exam=self.exam,
            question=self.question,
            answer="Boundary value analysis checks edge inputs.",
            identifier="A0000001",
        )

        SubjectiveReviewHistory.objects.create(
            subjective_answer=answer,
            operator="teacher001",
            old_score=None,
            new_score=6,
            old_comment="",
            new_comment="Clear but not complete.",
        )

        self.assertEqual(answer.review_status, "未阅")
        self.assertEqual(answer.anonymous_code, "ANSWER-000001")
        self.assertEqual(answer.histories.count(), 1)
