from django.core.cache import cache
from django.test import TestCase

from apps.research.services.live_workflow import (
    clear_workflow,
    get_workflow,
    run_defence,
    run_detection,
    run_evaluation,
    workflow_status,
)


class LiveResearchWorkflowStageTests(TestCase):
    def setUp(self):
        cache.clear()
        self.session_key = "test-live-research-session"

    def tearDown(self):
        clear_workflow(self.session_key)

    def test_empty_session_has_no_completed_stages(self):
        status = workflow_status(self.session_key)
        self.assertFalse(status["has_attack"])
        self.assertFalse(status["has_detection"])
        self.assertFalse(status["has_defence"])
        self.assertFalse(status["has_evaluation"])

    def test_detection_requires_attack(self):
        with self.assertRaisesRegex(ValueError, "Run an attack first"):
            run_detection(self.session_key)

    def test_defence_requires_attack(self):
        with self.assertRaisesRegex(ValueError, "Run an attack first"):
            run_defence(self.session_key)

    def test_evaluation_requires_attack(self):
        with self.assertRaisesRegex(ValueError, "Run an attack first"):
            run_evaluation(self.session_key)

    def test_clear_workflow_removes_cached_experiment(self):
        cache.set(
            f"rmrs:live-research:{self.session_key}",
            {"stage": "attack"},
            timeout=60,
        )
        self.assertIsNotNone(get_workflow(self.session_key))
        clear_workflow(self.session_key)
        self.assertIsNone(get_workflow(self.session_key))
