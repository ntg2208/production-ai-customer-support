"""
Evaluation Module for UKConnect Customer Support Agent

This module provides LLM-as-a-judge evaluation capabilities for assessing
agent response quality across multiple dimensions.

Components:
- criteria: Evaluation rubrics and scoring criteria
- prompts: Judge model prompt templates
- evaluator: Core evaluation logic
- reporter: Results aggregation and reporting
"""

from .criteria import (
    EvaluationCriterion,
    EVALUATION_CRITERIA,
    get_criterion_weights,
    PASS_THRESHOLD
)
from .evaluator import AgentEvaluator, EvaluationResult, SessionEvaluation
from .reporter import EvaluationReporter, EvaluationReport

__all__ = [
    # Criteria
    "EvaluationCriterion",
    "EVALUATION_CRITERIA",
    "get_criterion_weights",
    "PASS_THRESHOLD",
    # Evaluator
    "AgentEvaluator",
    "EvaluationResult",
    "SessionEvaluation",
    # Reporter
    "EvaluationReporter",
    "EvaluationReport",
]
