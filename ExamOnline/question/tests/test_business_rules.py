from django.test import RequestFactory, TestCase

from exam.models import Paper
from question.models import Choice, Fill, Judge, Subjective
from question.views import GeneratePaperAPIView, filter_by_subject, safe_level


class QuestionBankRuleTest(TestCase):
    def setUp(self):
        for index in range(3):
            Choice.objects.create(
                subject="Software Engineering",
                question=f"Choice {index}",
                answer_A="A",
                answer_B="B",
                answer_C="C",
                answer_D="D",
                right_answer="A",
                level="2",
            )
            Fill.objects.create(
                subject="Software Engineering",
                question=f"Fill {index}",
                right_answer="answer",
                level="2",
            )
            Judge.objects.create(
                subject="Software Engineering",
                question=f"Judge {index}",
                right_answer="T",
                level="2",
            )
            Subjective.objects.create(
                subject="Software Engineering",
                question=f"Subjective {index}",
                answer_template="template",
                level="2",
            )

    def test_question_default_scores_match_exam_rule(self):
        self.assertEqual(Choice.objects.first().score, 2)
        self.assertEqual(Fill.objects.first().score, 2)
        self.assertEqual(Judge.objects.first().score, 2)
        self.assertEqual(Subjective.objects.first().score, 8)

    def test_subject_filter_uses_fuzzy_match(self):
        queryset = filter_by_subject(Choice.objects.all(), "Engineering")

        self.assertEqual(queryset.count(), 3)

    def test_safe_level_falls_back_to_entry_level(self):
        self.assertEqual(safe_level(None), "1")
        self.assertEqual(safe_level(2), "2")

    def test_generate_paper_returns_all_configured_question_types(self):
        paper = Paper.objects.create(
            name="Generated Paper",
            subject="Software Engineering",
            choice_number=2,
            fill_number=1,
            judge_number=1,
            subjective_number=1,
            level="2",
        )
        request = RequestFactory().get("/api/paper/generate/", {"paper_id": paper.id})

        response = GeneratePaperAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["choice"]), 2)
        self.assertEqual(len(response.data["fill"]), 1)
        self.assertEqual(len(response.data["judge"]), 1)
        self.assertEqual(len(response.data["subjective"]), 1)

    def test_generate_paper_reports_missing_paper_id(self):
        request = RequestFactory().get("/api/paper/generate/")

        response = GeneratePaperAPIView.as_view()(request)

        self.assertEqual(response.status_code, 400)
