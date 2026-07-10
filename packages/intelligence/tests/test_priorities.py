from datetime import UTC, datetime, timedelta
from jarvis_intelligence.priorities import PriorityEngine, PriorityAssessment
from jarvis_intelligence.goals import Goal, GoalPriority, GoalState


class TestPriorityEngine:
    def test_assess_default_medium(self):
        engine = PriorityEngine()
        goal = Goal.create(description="Medium priority")
        assessment = engine.assess(goal)
        assert isinstance(assessment, PriorityAssessment)
        assert 0 <= assessment.overall_priority <= 1
        assert assessment.importance_score == 0.5

    def test_assess_critical(self):
        engine = PriorityEngine()
        goal = Goal.create(description="Critical goal", priority=GoalPriority.CRITICAL)
        assessment = engine.assess(goal)
        assert assessment.importance_score == 1.0
        assert assessment.overall_priority >= 0.6

    def test_assess_lowest(self):
        engine = PriorityEngine()
        goal = Goal.create(description="Lowest priority", priority=GoalPriority.LOWEST)
        assessment = engine.assess(goal)
        assert assessment.importance_score == 0.1

    def test_assess_with_deadline_urgent(self):
        engine = PriorityEngine()
        deadline = datetime.now(UTC) + timedelta(minutes=30)
        goal = Goal.create(
            description="Urgent", priority=GoalPriority.HIGH,
            deadline=deadline,
        )
        assessment = engine.assess(goal)
        assert assessment.urgency_score > 0.7

    def test_assess_with_deadline_future(self):
        engine = PriorityEngine()
        deadline = datetime.now(UTC) + timedelta(days=30)
        goal = Goal.create(
            description="Future", priority=GoalPriority.LOW,
            deadline=deadline,
        )
        assessment = engine.assess(goal)
        assert assessment.urgency_score < 0.6

    def test_assess_in_progress(self):
        engine = PriorityEngine()
        goal = Goal.create(description="In progress", priority=GoalPriority.MEDIUM)
        assessment_in_progress = engine.assess(
            Goal(
                id=goal.id, description=goal.description,
                priority=goal.priority, state=GoalState.IN_PROGRESS,
            )
        )
        assessment_draft = engine.assess(goal)
        assert assessment_in_progress.urgency_score > assessment_draft.urgency_score

    def test_assess_with_dependencies(self):
        engine = PriorityEngine()
        goal = Goal.create(
            description="With deps", priority=GoalPriority.MEDIUM,
            dependencies=("g1", "g2", "g3"),
        )
        assessment = engine.assess(goal)
        assert "dependency_count" in assessment.factors
        assert assessment.factors["dependency_count"] > 0

    def test_deadline_factor_no_deadline(self):
        engine = PriorityEngine()
        goal = Goal.create(description="No deadline")
        factor = engine._deadline_factor(goal)
        assert factor == 0.0

    def test_deadline_factor_overdue(self):
        engine = PriorityEngine()
        goal = Goal.create(
            description="Overdue",
            deadline=datetime.now(UTC) - timedelta(hours=1),
        )
        factor = engine._deadline_factor(goal)
        assert factor == 1.0

    def test_priority_assessment_dataclass(self):
        assessment = PriorityAssessment(
            goal_id="g1", urgency_score=0.8,
            importance_score=0.6, overall_priority=0.68,
            factors={"deadline": 0.2},
        )
        assert assessment.goal_id == "g1"
        assert assessment.overall_priority == 0.68
