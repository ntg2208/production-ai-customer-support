"""
Evaluation Reporter

Aggregates evaluation results and generates reports in various formats.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .evaluator import EvaluationResult, SessionEvaluation
from .criteria import EVALUATION_CRITERIA, PASS_THRESHOLD


@dataclass
class EvaluationReport:
    """Complete evaluation report across multiple sessions"""
    report_id: str
    generated_at: str
    total_sessions: int
    total_turns: int
    overall_pass_rate: float
    overall_score: float
    scores_by_criterion: Dict[str, float]
    scores_by_session: Dict[str, float]
    sessions: List[SessionEvaluation]
    top_issues: List[Dict[str, Any]]
    top_strengths: List[str]
    criterion_distribution: Dict[str, Dict[str, int]]  # criterion -> {1: count, 2: count, ...}
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "summary": {
                "total_sessions": self.total_sessions,
                "total_turns": self.total_turns,
                "overall_pass_rate": self.overall_pass_rate,
                "overall_score": self.overall_score,
                "pass_threshold": PASS_THRESHOLD
            },
            "scores_by_criterion": self.scores_by_criterion,
            "scores_by_session": self.scores_by_session,
            "sessions": [s.to_dict() for s in self.sessions],
            "top_issues": self.top_issues,
            "top_strengths": self.top_strengths,
            "criterion_distribution": self.criterion_distribution,
            "recommendations": self.recommendations
        }


class EvaluationReporter:
    """
    Generates evaluation reports from session evaluations.
    """

    def __init__(self, output_dir: str = "evaluation_results"):
        """
        Initialize reporter.

        Args:
            output_dir: Directory for saving reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        sessions: List[SessionEvaluation],
        report_id: Optional[str] = None
    ) -> EvaluationReport:
        """
        Generate a comprehensive report from session evaluations.

        Args:
            sessions: List of session evaluations
            report_id: Optional report identifier

        Returns:
            EvaluationReport with aggregated metrics
        """
        report_id = report_id or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate totals
        total_sessions = len(sessions)
        total_turns = sum(s.total_turns for s in sessions)
        passed_sessions = sum(1 for s in sessions if s.pass_fail)
        overall_pass_rate = (passed_sessions / total_sessions * 100) if total_sessions > 0 else 0

        # Aggregate scores by criterion
        scores_by_criterion = {}
        for criterion in EVALUATION_CRITERIA:
            scores = [s.aggregate_scores.get(criterion, 0) for s in sessions]
            scores_by_criterion[criterion] = round(sum(scores) / len(scores), 2) if scores else 0

        # Scores by session
        scores_by_session = {s.session_id: s.overall_score for s in sessions}

        # Overall score
        overall_score = round(sum(s.overall_score for s in sessions) / len(sessions), 2) if sessions else 0

        # Collect all issues with frequency
        issue_counts: Dict[str, int] = {}
        for session in sessions:
            for issue in session.key_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        top_issues = [
            {"issue": issue, "frequency": count, "percentage": round(count / total_sessions * 100, 1)}
            for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1])[:10]
        ]

        # Collect strengths
        strength_counts: Dict[str, int] = {}
        for session in sessions:
            for strength in session.key_strengths:
                strength_counts[strength] = strength_counts.get(strength, 0) + 1

        top_strengths = [s for s, _ in sorted(strength_counts.items(), key=lambda x: -x[1])[:5]]

        # Score distribution by criterion
        criterion_distribution = {}
        for criterion in EVALUATION_CRITERIA:
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for session in sessions:
                for turn in session.turn_results:
                    score = round(turn.scores.get(criterion, 3))
                    score = max(1, min(5, score))  # Clamp to 1-5
                    distribution[score] += 1
            criterion_distribution[criterion] = distribution

        # Generate recommendations
        recommendations = self._generate_recommendations(scores_by_criterion, top_issues)

        return EvaluationReport(
            report_id=report_id,
            generated_at=datetime.now().isoformat(),
            total_sessions=total_sessions,
            total_turns=total_turns,
            overall_pass_rate=overall_pass_rate,
            overall_score=overall_score,
            scores_by_criterion=scores_by_criterion,
            scores_by_session=scores_by_session,
            sessions=sessions,
            top_issues=top_issues,
            top_strengths=top_strengths,
            criterion_distribution=criterion_distribution,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        scores: Dict[str, float],
        issues: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations based on scores and issues"""
        recommendations = []

        # Check each criterion
        if scores.get("accuracy", 5) < 4:
            recommendations.append(
                "Improve factual accuracy: Review RAG retrieval quality and consider "
                "expanding the knowledge base with more specific policy details."
            )

        if scores.get("helpfulness", 5) < 4:
            recommendations.append(
                "Enhance helpfulness: Train agents to ask clarifying questions "
                "and provide more comprehensive solutions."
            )

        if scores.get("task_completion", 5) < 4:
            recommendations.append(
                "Improve task completion: Review tool execution reliability "
                "and add confirmation steps for critical operations."
            )

        if scores.get("tone", 5) < 4:
            recommendations.append(
                "Refine tone: Update agent instructions to better match "
                "customer communication styles (formal vs casual)."
            )

        if scores.get("routing", 5) < 4:
            recommendations.append(
                "Optimize routing: Review master agent delegation logic "
                "and improve intent classification accuracy."
            )

        if scores.get("policy_adherence", 5) < 4:
            recommendations.append(
                "Strengthen policy adherence: Update policy agent prompts "
                "and ensure RAG retrieves current policy information."
            )

        # Add issue-specific recommendations
        issue_keywords = {
            "hallucin": "Add fact-checking guardrails to prevent hallucinations.",
            "timeout": "Optimize agent response times and add timeout handling.",
            "context": "Improve context retention across conversation turns.",
            "routing": "Refine agent selection criteria in master agent.",
        }

        for issue_info in issues[:3]:
            issue_text = issue_info["issue"].lower()
            for keyword, recommendation in issue_keywords.items():
                if keyword in issue_text and recommendation not in recommendations:
                    recommendations.append(recommendation)

        return recommendations[:7]  # Limit to top 7 recommendations

    def export_json(self, report: EvaluationReport, filename: Optional[str] = None) -> str:
        """Export report to JSON file"""
        filename = filename or f"{report.report_id}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

        return str(filepath)

    def export_markdown(self, report: EvaluationReport, filename: Optional[str] = None) -> str:
        """Export report to Markdown file"""
        filename = filename or f"{report.report_id}.md"
        filepath = self.output_dir / filename

        md = self._generate_markdown(report)

        with open(filepath, 'w') as f:
            f.write(md)

        return str(filepath)

    def _generate_markdown(self, report: EvaluationReport) -> str:
        """Generate Markdown report content"""
        lines = [
            f"# Agent Evaluation Report",
            f"",
            f"**Report ID**: {report.report_id}",
            f"**Generated**: {report.generated_at}",
            f"",
            f"---",
            f"",
            f"## Executive Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Sessions | {report.total_sessions} |",
            f"| Total Turns | {report.total_turns} |",
            f"| Overall Score | {report.overall_score:.2f} / 5.00 |",
            f"| Pass Rate | {report.overall_pass_rate:.1f}% |",
            f"| Pass Threshold | {PASS_THRESHOLD} |",
            f"",
            f"### Overall Assessment: {'PASS' if report.overall_score >= PASS_THRESHOLD else 'NEEDS IMPROVEMENT'}",
            f"",
            f"---",
            f"",
            f"## Scores by Criterion",
            f"",
            f"| Criterion | Score | Status |",
            f"|-----------|-------|--------|",
        ]

        for criterion, score in sorted(report.scores_by_criterion.items(), key=lambda x: -x[1]):
            status = "Good" if score >= 4 else ("Acceptable" if score >= 3 else "Needs Work")
            bar = "" * int(score) + "" * (5 - int(score))
            lines.append(f"| {criterion.replace('_', ' ').title()} | {score:.2f} {bar} | {status} |")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## Session Results",
            f"",
            f"| Session | Score | Pass/Fail | Turns |",
            f"|---------|-------|-----------|-------|",
        ])

        for session in sorted(report.sessions, key=lambda s: -s.overall_score):
            status = "PASS" if session.pass_fail else "FAIL"
            lines.append(
                f"| {session.session_title[:40]} | {session.overall_score:.2f} | {status} | "
                f"{session.passed_turns}/{session.total_turns} |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## Top Issues",
            f"",
        ])

        if report.top_issues:
            for i, issue in enumerate(report.top_issues[:5], 1):
                lines.append(f"{i}. **{issue['issue']}** ({issue['frequency']} occurrences, {issue['percentage']}%)")
        else:
            lines.append("No significant issues identified.")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## Key Strengths",
            f"",
        ])

        if report.top_strengths:
            for strength in report.top_strengths:
                lines.append(f"- {strength}")
        else:
            lines.append("No specific strengths highlighted.")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## Recommendations",
            f"",
        ])

        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## Score Distribution",
            f"",
        ])

        for criterion, dist in report.criterion_distribution.items():
            total = sum(dist.values())
            if total > 0:
                lines.append(f"### {criterion.replace('_', ' ').title()}")
                lines.append(f"")
                for score in range(5, 0, -1):
                    count = dist.get(score, 0)
                    pct = count / total * 100
                    bar = "" * int(pct / 5)
                    lines.append(f"- {score}: {bar} {count} ({pct:.0f}%)")
                lines.append(f"")

        lines.extend([
            f"---",
            f"",
            f"*Report generated by UKConnect Agent Evaluation System*",
        ])

        return "\n".join(lines)

    def print_summary(self, report: EvaluationReport):
        """Print a summary to console"""
        print("\n" + "=" * 60)
        print("EVALUATION REPORT SUMMARY")
        print("=" * 60)
        print(f"Report ID: {report.report_id}")
        print(f"Sessions: {report.total_sessions} | Turns: {report.total_turns}")
        print(f"Overall Score: {report.overall_score:.2f} / 5.00")
        print(f"Pass Rate: {report.overall_pass_rate:.1f}%")
        print("-" * 60)
        print("Scores by Criterion:")
        for criterion, score in sorted(report.scores_by_criterion.items(), key=lambda x: -x[1]):
            bar = "" * int(score) + "" * (5 - int(score))
            print(f"  {criterion:20s}: {score:.2f} {bar}")
        print("-" * 60)
        if report.top_issues:
            print("Top Issues:")
            for issue in report.top_issues[:3]:
                print(f"  - {issue['issue']} ({issue['frequency']}x)")
        print("-" * 60)
        if report.recommendations:
            print("Recommendations:")
            for rec in report.recommendations[:3]:
                print(f"  - {rec[:70]}...")
        print("=" * 60)
