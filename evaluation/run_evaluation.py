#!/usr/bin/env python3
"""
Evaluation Runner CLI

Command-line interface for running agent evaluations with LLM-as-a-judge.

Usage:
    python -m evaluation.run_evaluation                    # Run quick evaluation (3 sessions)
    python -m evaluation.run_evaluation --session 1        # Evaluate specific session
    python -m evaluation.run_evaluation --all              # Evaluate all sessions
    python -m evaluation.run_evaluation --compare          # Compare two model responses
    python -m evaluation.run_evaluation --safety-audit     # Run safety audit on sessions
"""

import sys
import os
import asyncio
import argparse
import json
import time
from datetime import datetime
from typing import List, Tuple, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv()

# Terminal colors
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    GREEN_BOLD = '\033[32m\033[1m'
    RED_BOLD = '\033[31m\033[1m'
    YELLOW_BOLD = '\033[33m\033[1m'
    CYAN_BOLD = '\033[36m\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.CYAN_BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN_BOLD}{text}{Colors.RESET}")
    print(f"{Colors.CYAN_BOLD}{'=' * 60}{Colors.RESET}\n")


def print_progress(current: int, total: int, text: str):
    """Print progress indicator"""
    pct = current / total * 100 if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * current / total) if total > 0 else 0
    bar = '' * filled + '' * (bar_len - filled)
    print(f"\r{Colors.BLUE}[{bar}] {pct:.0f}% - {text}{Colors.RESET}", end='', flush=True)


async def run_agent_session(
    session_key: str,
    session_data: dict
) -> List[Tuple[str, str]]:
    """
    Run a test session through the agent and collect responses.

    Returns list of (user_input, agent_response) tuples.
    """
    from agent import get_master_agent
    from google.adk.sessions import InMemorySessionService
    from google.adk import Runner
    from google.genai.types import Content, Part

    # Initialize agent
    master_agent = get_master_agent()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=master_agent,
        session_service=session_service,
        app_name="ukconnect_evaluation"
    )

    # Setup customer state
    try:
        from utils.customer_setup import setup_customer_for_session
        customer_state = await setup_customer_for_session(session_key)
    except Exception:
        customer_state = {
            "user_email": session_data.get("customer_email", "test@test.com"),
            "user_information": {
                "name": session_data.get("customer_name", "Test User"),
                "customer_id": session_data.get("customer_id", "TEST001")
            },
            "active_ticket_reference": [],
            "history_transaction": [],
            "date_time": datetime.now().strftime("%A %Y-%m-%d %H:%M GMT")
        }

    # Create session
    session = await session_service.create_session(
        app_name="ukconnect_evaluation",
        user_id=customer_state.get("user_email", "test@test.com"),
        state=customer_state
    )

    # Run through messages
    conversations = []
    messages = session_data.get("messages", [])

    for i, message in enumerate(messages):
        print_progress(i + 1, len(messages), f"Processing message {i + 1}/{len(messages)}")

        try:
            content = Content(role='user', parts=[Part(text=message)])
            events = runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content
            )

            response = "No response generated"
            async for event in events:
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                        response = event.content.parts[0].text
                        break

            conversations.append((message, response))

            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)

        except Exception as e:
            conversations.append((message, f"Error: {str(e)}"))

    print()  # New line after progress bar
    return conversations


async def evaluate_session(
    evaluator,
    session_key: str,
    session_data: dict,
    conversations: List[Tuple[str, str]]
) -> 'SessionEvaluation':
    """Evaluate a single session"""
    from evaluation.evaluator import SessionEvaluation

    metadata = {
        "customer_name": session_data.get("customer_name", "Unknown"),
        "customer_id": session_data.get("customer_id", "N/A"),
        "title": session_data.get("title", session_key),
        "expected_agents": session_data.get("expected_agents", ["master_agent"]),
        "key_functionality": session_data.get("key_functionality", []),
        "session_type": "casual" if int(session_key.split('_')[1]) > 10 else "formal"
    }

    return await evaluator.evaluate_session(
        session_id=session_key,
        conversation=conversations,
        session_metadata=metadata
    )


async def main():
    """Main evaluation runner"""
    parser = argparse.ArgumentParser(
        description="UKConnect Agent Evaluation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m evaluation.run_evaluation                    # Quick evaluation
    python -m evaluation.run_evaluation --session 1        # Single session
    python -m evaluation.run_evaluation --all              # All sessions
    python -m evaluation.run_evaluation --from-file results.json  # Evaluate saved results
        """
    )

    parser.add_argument('--session', '-s',
                        help='Evaluate specific session (by number 1-15 or by name)')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Evaluate all test sessions')
    parser.add_argument('--quick', '-q', action='store_true',
                        help='Quick evaluation (sessions 1, 5, 11)')
    parser.add_argument('--from-file', '-f',
                        help='Evaluate from saved conversation JSON file')
    parser.add_argument('--judge-model', default='models/gemini-2.0-flash',
                        help='Model to use as judge (default: models/gemini-2.0-flash)')
    parser.add_argument('--output', '-o',
                        help='Output directory for reports (default: evaluation_results)')
    parser.add_argument('--format', choices=['json', 'markdown', 'both'], default='both',
                        help='Output format (default: both)')
    parser.add_argument('--no-run', action='store_true',
                        help='Skip running agent, use cached/provided conversations')
    parser.add_argument('--safety-audit', action='store_true',
                        help='Include safety audit in evaluation')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    print_header("UKConnect Agent Evaluation System")
    print(f"Judge Model: {args.judge_model}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Import evaluation modules
    from evaluation.evaluator import AgentEvaluator
    from evaluation.reporter import EvaluationReporter
    from test_message_scenarios import get_all_sessions

    # Initialize evaluator and reporter
    try:
        evaluator = AgentEvaluator(judge_model=args.judge_model)
        print(f"{Colors.GREEN}Evaluator initialized successfully{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED_BOLD}Failed to initialize evaluator: {e}{Colors.RESET}")
        sys.exit(1)

    output_dir = args.output or "evaluation_results"
    reporter = EvaluationReporter(output_dir=output_dir)

    # Determine which sessions to evaluate
    all_sessions = get_all_sessions()
    sessions_to_run = []

    if args.from_file:
        # Load conversations from file
        print(f"Loading conversations from: {args.from_file}")
        with open(args.from_file, 'r') as f:
            saved_data = json.load(f)
        # Process saved data format
        # (Implementation depends on saved format)
        print(f"{Colors.YELLOW}--from-file not fully implemented yet{Colors.RESET}")
        sys.exit(1)

    elif args.session:
        # Single session
        session_key = args.session
        if session_key.isdigit():
            session_num = int(session_key)
            session_keys = list(all_sessions.keys())
            if 1 <= session_num <= len(session_keys):
                session_key = session_keys[session_num - 1]
            else:
                print(f"{Colors.RED}Session number must be between 1 and {len(session_keys)}{Colors.RESET}")
                sys.exit(1)

        if session_key in all_sessions:
            sessions_to_run = [(session_key, all_sessions[session_key])]
        else:
            print(f"{Colors.RED}Session '{session_key}' not found{Colors.RESET}")
            sys.exit(1)

    elif args.all:
        sessions_to_run = list(all_sessions.items())

    else:
        # Quick mode - sessions 1, 5, 11
        quick_sessions = ['session_1_new_customer', 'session_5_problem_resolution', 'session_11_casual_student']
        sessions_to_run = [(k, all_sessions[k]) for k in quick_sessions if k in all_sessions]

    print(f"\nSessions to evaluate: {len(sessions_to_run)}")
    total_messages = sum(len(s[1]['messages']) for s in sessions_to_run)
    print(f"Total messages: {total_messages}")
    print(f"Estimated time: {total_messages * 5} seconds\n")

    # Run evaluations
    session_evaluations = []
    start_time = time.time()

    for i, (session_key, session_data) in enumerate(sessions_to_run, 1):
        print_header(f"Session {i}/{len(sessions_to_run)}: {session_data['title']}")
        print(f"Customer: {session_data.get('customer_name', 'Unknown')}")
        print(f"Messages: {len(session_data['messages'])}")

        # Run agent or use cached conversations
        if not args.no_run:
            print(f"\n{Colors.BLUE}Running agent...{Colors.RESET}")
            try:
                conversations = await run_agent_session(session_key, session_data)
            except Exception as e:
                print(f"{Colors.RED}Failed to run session: {e}{Colors.RESET}")
                continue
        else:
            print(f"{Colors.YELLOW}Skipping agent run (--no-run){Colors.RESET}")
            continue

        # Evaluate
        print(f"\n{Colors.BLUE}Evaluating responses...{Colors.RESET}")
        try:
            evaluation = await evaluate_session(evaluator, session_key, session_data, conversations)
            session_evaluations.append(evaluation)

            # Print quick results
            status = f"{Colors.GREEN_BOLD}PASS{Colors.RESET}" if evaluation.pass_fail else f"{Colors.RED_BOLD}FAIL{Colors.RESET}"
            print(f"\nResult: {status}")
            print(f"Score: {evaluation.overall_score:.2f} / 5.00")
            print(f"Turns passed: {evaluation.passed_turns}/{evaluation.total_turns}")

            if evaluation.key_issues and args.verbose:
                print(f"Issues: {', '.join(evaluation.key_issues[:2])}")

        except Exception as e:
            print(f"{Colors.RED}Evaluation failed: {e}{Colors.RESET}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    # Generate report
    if session_evaluations:
        print_header("Generating Report")

        report = reporter.generate_report(session_evaluations)

        # Export
        if args.format in ['json', 'both']:
            json_path = reporter.export_json(report)
            print(f"JSON report: {json_path}")

        if args.format in ['markdown', 'both']:
            md_path = reporter.export_markdown(report)
            print(f"Markdown report: {md_path}")

        # Print summary
        reporter.print_summary(report)

    elapsed = time.time() - start_time
    print(f"\n{Colors.GREEN}Evaluation completed in {elapsed:.1f} seconds{Colors.RESET}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Evaluation interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED_BOLD}Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
