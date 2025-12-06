"""
Core Evaluator for LLM-as-a-Judge Evaluation

This module provides the main evaluation logic using an LLM judge
to assess agent response quality.
"""

import json
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import os
import re

try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    genai_types = None
    GENAI_AVAILABLE = False

from .criteria import (
    EVALUATION_CRITERIA,
    get_criterion_weights,
    PASS_THRESHOLD,
    MINIMUM_SCORES
)
from .prompts import build_evaluation_prompt


@dataclass
class EvaluationResult:
    """Result of evaluating a single turn"""
    session_id: str
    turn_index: int
    user_input: str
    agent_response: str
    scores: Dict[str, float]
    overall_score: float
    reasoning: str
    issues: List[str]
    strengths: List[str]
    pass_fail: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    evaluation_latency_ms: float = 0.0
    raw_judge_response: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "user_input": self.user_input,
            "agent_response": self.agent_response,
            "scores": self.scores,
            "overall_score": self.overall_score,
            "reasoning": self.reasoning,
            "issues": self.issues,
            "strengths": self.strengths,
            "pass_fail": self.pass_fail,
            "timestamp": self.timestamp,
            "evaluation_latency_ms": self.evaluation_latency_ms
        }

    def get_failed_criteria(self) -> List[str]:
        """Get list of criteria that fell below minimum threshold"""
        failed = []
        for criterion, min_score in MINIMUM_SCORES.items():
            if self.scores.get(criterion, 0) < min_score:
                failed.append(criterion)
        return failed


@dataclass
class SessionEvaluation:
    """Aggregated evaluation for an entire session"""
    session_id: str
    session_title: str
    customer_name: str
    turn_results: List[EvaluationResult]
    aggregate_scores: Dict[str, float]
    overall_score: float
    conversation_flow_score: float
    context_retention_score: float
    pass_fail: bool
    total_turns: int
    passed_turns: int
    failed_turns: int
    key_issues: List[str]
    key_strengths: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "session_title": self.session_title,
            "customer_name": self.customer_name,
            "turn_results": [r.to_dict() for r in self.turn_results],
            "aggregate_scores": self.aggregate_scores,
            "overall_score": self.overall_score,
            "conversation_flow_score": self.conversation_flow_score,
            "context_retention_score": self.context_retention_score,
            "pass_fail": self.pass_fail,
            "total_turns": self.total_turns,
            "passed_turns": self.passed_turns,
            "failed_turns": self.failed_turns,
            "key_issues": self.key_issues,
            "key_strengths": self.key_strengths,
            "timestamp": self.timestamp
        }


class AgentEvaluator:
    """
    LLM-as-a-Judge evaluator for agent responses.

    Uses a separate LLM (the "judge") to evaluate agent response quality
    across multiple dimensions.
    """

    def __init__(
        self,
        judge_model: str = "models/gemini-2.0-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.1,  # Low temperature for consistent evaluation
        max_retries: int = 3
    ):
        """
        Initialize the evaluator.

        Args:
            judge_model: Model ID for the judge LLM
            api_key: API key (uses GOOGLE_API_KEY env var if not provided)
            temperature: Temperature for judge responses (lower = more consistent)
            max_retries: Number of retries for failed evaluations
        """
        self.judge_model = judge_model
        self.temperature = temperature
        self.max_retries = max_retries
        self.weights = get_criterion_weights()

        # Initialize the judge model
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai is required for evaluation. Install with: pip install google-genai")

        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        # Initialize the client
        self.client = genai.Client(api_key=api_key)

        # Generation config for consistent evaluation
        self.generation_config = genai_types.GenerateContentConfig(
            temperature=temperature,
            top_p=0.95,
            response_mime_type="application/json"
        )

    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted average score"""
        total_weight = 0.0
        weighted_sum = 0.0

        for criterion, score in scores.items():
            weight = self.weights.get(criterion, 0.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return round(weighted_sum / total_weight, 2)

    def _parse_judge_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the judge's JSON response with error handling"""
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to find JSON object in text
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

            # Return default structure if parsing fails
            return {
                "scores": {c: 3 for c in EVALUATION_CRITERIA},
                "overall_score": 3.0,
                "reasoning": f"Failed to parse judge response: {response_text[:200]}",
                "issues": ["Evaluation parsing failed"],
                "strengths": [],
                "pass": False
            }

    async def evaluate_turn(
        self,
        user_input: str,
        agent_response: str,
        session_id: str,
        turn_index: int,
        context: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate a single conversation turn.

        Args:
            user_input: The user's message
            agent_response: The agent's response
            session_id: Identifier for the session
            turn_index: Index of this turn in the conversation
            context: Additional context (customer info, session metadata)

        Returns:
            EvaluationResult with scores and analysis
        """
        context = context or {}
        start_time = datetime.now()

        # Build the evaluation prompt
        prompt = build_evaluation_prompt(
            prompt_type="single_turn",
            user_input=user_input,
            agent_response=agent_response,
            customer_name=context.get("customer_name", "Unknown"),
            customer_id=context.get("customer_id", "N/A"),
            query_type=context.get("query_type", "general"),
            expected_agents=", ".join(context.get("expected_agents", ["master_agent"])),
            session_type=context.get("session_type", "formal"),
            customer_state=json.dumps(context.get("customer_state", {}), indent=2)
        )

        # Call the judge with retries
        raw_response = ""
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.judge_model,
                    contents=prompt,
                    config=self.generation_config
                )
                raw_response = response.text
                break
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raw_response = json.dumps({
                        "scores": {c: 3 for c in EVALUATION_CRITERIA},
                        "overall_score": 3.0,
                        "reasoning": f"Judge call failed: {str(e)}",
                        "issues": ["Evaluation failed due to API error"],
                        "strengths": [],
                        "pass": False
                    })
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

        # Parse the response
        parsed = self._parse_judge_response(raw_response)

        # Extract scores
        scores = parsed.get("scores", {})
        # Ensure all criteria are present
        for criterion in EVALUATION_CRITERIA:
            if criterion not in scores:
                scores[criterion] = 3  # Default to middle score

        # Calculate weighted overall score if not provided
        overall = parsed.get("overall_score")
        if overall is None:
            overall = self._calculate_weighted_score(scores)

        latency = (datetime.now() - start_time).total_seconds() * 1000

        return EvaluationResult(
            session_id=session_id,
            turn_index=turn_index,
            user_input=user_input,
            agent_response=agent_response,
            scores=scores,
            overall_score=overall,
            reasoning=parsed.get("reasoning", ""),
            issues=parsed.get("issues", []),
            strengths=parsed.get("strengths", []),
            pass_fail=parsed.get("pass", overall >= PASS_THRESHOLD),
            evaluation_latency_ms=latency,
            raw_judge_response=raw_response
        )

    async def evaluate_session(
        self,
        session_id: str,
        conversation: List[Tuple[str, str]],  # List of (user_input, agent_response)
        session_metadata: Optional[Dict[str, Any]] = None
    ) -> SessionEvaluation:
        """
        Evaluate an entire conversation session.

        Args:
            session_id: Identifier for the session
            conversation: List of (user_input, agent_response) tuples
            session_metadata: Metadata about the session (title, customer, etc.)

        Returns:
            SessionEvaluation with aggregated results
        """
        metadata = session_metadata or {}

        # Evaluate each turn
        turn_results = []
        for i, (user_input, agent_response) in enumerate(conversation):
            result = await self.evaluate_turn(
                user_input=user_input,
                agent_response=agent_response,
                session_id=session_id,
                turn_index=i,
                context=metadata
            )
            turn_results.append(result)

        # Aggregate scores across turns
        aggregate_scores = {}
        for criterion in EVALUATION_CRITERIA:
            scores = [r.scores.get(criterion, 3) for r in turn_results]
            aggregate_scores[criterion] = round(sum(scores) / len(scores), 2) if scores else 0

        overall = self._calculate_weighted_score(aggregate_scores)

        # Count pass/fail
        passed = sum(1 for r in turn_results if r.pass_fail)
        failed = len(turn_results) - passed

        # Collect issues and strengths
        all_issues = []
        all_strengths = []
        for r in turn_results:
            all_issues.extend(r.issues)
            all_strengths.extend(r.strengths)

        # Deduplicate and take top issues/strengths
        key_issues = list(dict.fromkeys(all_issues))[:5]
        key_strengths = list(dict.fromkeys(all_strengths))[:5]

        # Evaluate conversation as a whole (optional multi-turn evaluation)
        flow_score = 4.0  # Default
        context_score = 4.0  # Default

        # Build conversation history for multi-turn evaluation
        conv_history = "\n\n".join([
            f"**Turn {i+1}**\nUser: {user}\nAgent: {agent}"
            for i, (user, agent) in enumerate(conversation)
        ])

        try:
            multi_turn_prompt = build_evaluation_prompt(
                prompt_type="multi_turn",
                user_input="",
                agent_response="",
                customer_name=metadata.get("customer_name", "Unknown"),
                customer_id=metadata.get("customer_id", "N/A"),
                session_title=metadata.get("title", session_id),
                key_functionality=", ".join(metadata.get("key_functionality", [])),
                conversation_history=conv_history
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.judge_model,
                contents=multi_turn_prompt,
                config=self.generation_config
            )
            multi_parsed = self._parse_judge_response(response.text)
            flow_score = multi_parsed.get("conversation_flow_score", 4.0)
            context_score = multi_parsed.get("context_retention_score", 4.0)

            # Add multi-turn specific issues
            for turn_issue in multi_parsed.get("turn_issues", []):
                issue_desc = f"Turn {turn_issue.get('turn', '?')}: {turn_issue.get('issue', '')}"
                if issue_desc not in key_issues:
                    key_issues.append(issue_desc)

        except Exception:
            pass  # Use defaults if multi-turn eval fails

        return SessionEvaluation(
            session_id=session_id,
            session_title=metadata.get("title", session_id),
            customer_name=metadata.get("customer_name", "Unknown"),
            turn_results=turn_results,
            aggregate_scores=aggregate_scores,
            overall_score=overall,
            conversation_flow_score=flow_score,
            context_retention_score=context_score,
            pass_fail=overall >= PASS_THRESHOLD and failed <= len(turn_results) * 0.3,
            total_turns=len(turn_results),
            passed_turns=passed,
            failed_turns=failed,
            key_issues=key_issues[:5],
            key_strengths=key_strengths[:5]
        )

    async def safety_audit(
        self,
        user_input: str,
        agent_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform a safety audit on a response.

        Args:
            user_input: The user's message
            agent_response: The agent's response
            context: Additional context

        Returns:
            Safety audit results
        """
        context = context or {}

        prompt = build_evaluation_prompt(
            prompt_type="safety",
            user_input=user_input,
            agent_response=agent_response,
            customer_name=context.get("customer_name", "Unknown")
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.judge_model,
                contents=prompt,
                config=self.generation_config
            )
            return self._parse_judge_response(response.text)
        except Exception as e:
            return {
                "safe": True,  # Default to safe on error
                "issues": [],
                "data_exposure_risk": "unknown",
                "reasoning": f"Safety audit failed: {str(e)}"
            }

    async def compare_responses(
        self,
        user_input: str,
        response_a: str,
        response_b: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare two agent responses to the same input.

        Args:
            user_input: The user's message
            response_a: First response to compare
            response_b: Second response to compare
            context: Additional context

        Returns:
            Comparison results including winner and reasoning
        """
        context = context or {}

        prompt = build_evaluation_prompt(
            prompt_type="comparative",
            user_input=user_input,
            agent_response=response_b,
            customer_name=context.get("customer_name", "Unknown"),
            query_type=context.get("query_type", "general"),
            response_a=response_a,
            response_b=response_b
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.judge_model,
                contents=prompt,
                config=self.generation_config
            )
            return self._parse_judge_response(response.text)
        except Exception as e:
            return {
                "winner": "TIE",
                "reasoning": f"Comparison failed: {str(e)}",
                "key_differences": []
            }
