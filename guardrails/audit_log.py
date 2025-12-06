"""
Guardrail Logging

Provides logging and auditing for guardrail operations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .filters import FilterResult, RiskLevel


class GuardrailLogger:
    """
    Logs guardrail operations for auditing and monitoring.

    Tracks:
    - Input checks (what was filtered/blocked)
    - Output checks (what was modified/blocked)
    - Tool validations
    - Errors and exceptions
    """

    def __init__(
        self,
        log_file: str = "guardrails.log",
        enabled: bool = True,
        log_to_console: bool = False
    ):
        """
        Initialize guardrail logger.

        Args:
            log_file: Path to log file
            enabled: Whether logging is enabled
            log_to_console: Also log to console
        """
        self.enabled = enabled
        self.log_file = Path(log_file)

        if enabled:
            # Ensure log directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

            # Setup logger
            self.logger = logging.getLogger("guardrails")
            self.logger.setLevel(logging.INFO)

            # File handler
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

            # Console handler (optional)
            if log_to_console:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.WARNING)
                console_handler.setFormatter(file_format)
                self.logger.addHandler(console_handler)

    def _log(self, level: str, event_type: str, data: Dict[str, Any]):
        """Internal logging method"""
        if not self.enabled:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            **data
        }

        message = json.dumps(entry)

        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)

    def log_input_check(
        self,
        message: str,
        result: FilterResult,
        agent_name: str = "unknown"
    ):
        """Log an input validation check"""
        level = "warning" if not result.is_safe else "info"

        self._log(level, "input_check", {
            "agent": agent_name,
            "message_preview": message[:100] + "..." if len(message) > 100 else message,
            "is_safe": result.is_safe,
            "risk_level": result.risk_level.value,
            "detected_count": len(result.detected_items),
            "detected_types": list(set(item.get("type", "unknown") for item in result.detected_items)),
            "explanation": result.explanation
        })

    def log_output_check(
        self,
        response: str,
        result: FilterResult,
        agent_name: str = "unknown"
    ):
        """Log an output validation check"""
        level = "warning" if not result.is_safe else "info"

        self._log(level, "output_check", {
            "agent": agent_name,
            "response_preview": response[:100] + "..." if len(response) > 100 else response,
            "is_safe": result.is_safe,
            "risk_level": result.risk_level.value,
            "detected_count": len(result.detected_items),
            "was_sanitized": result.sanitized_text is not None,
            "explanation": result.explanation
        })

    def log_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any]
    ):
        """Log a tool call (successful validation)"""
        # Sanitize args for logging (don't log sensitive data)
        safe_args = {}
        for key, value in args.items():
            if any(sensitive in key.lower() for sensitive in ["password", "token", "secret", "key"]):
                safe_args[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 50:
                safe_args[key] = value[:50] + "..."
            else:
                safe_args[key] = value

        self._log("info", "tool_call", {
            "tool_name": tool_name,
            "args": safe_args,
            "status": "allowed"
        })

    def log_tool_block(
        self,
        tool_name: str,
        reason: str
    ):
        """Log a blocked tool call"""
        self._log("warning", "tool_blocked", {
            "tool_name": tool_name,
            "reason": reason,
            "status": "blocked"
        })

    def log_error(
        self,
        callback_type: str,
        error_message: str
    ):
        """Log a guardrail error"""
        self._log("error", "guardrail_error", {
            "callback_type": callback_type,
            "error": error_message
        })

    def log_block(
        self,
        block_type: str,
        reason: str,
        risk_level: RiskLevel,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log a content block"""
        self._log("warning", "content_blocked", {
            "block_type": block_type,
            "reason": reason,
            "risk_level": risk_level.value,
            "details": details or {}
        })

    def get_stats(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get statistics from the log file.

        Args:
            since: Only count entries since this time

        Returns:
            Statistics dictionary
        """
        if not self.enabled or not self.log_file.exists():
            return {"error": "Logging not enabled or no log file"}

        stats = {
            "total_checks": 0,
            "input_checks": 0,
            "output_checks": 0,
            "tool_calls": 0,
            "blocks": 0,
            "errors": 0,
            "risk_levels": {
                "none": 0,
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            }
        }

        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        # Extract JSON from log line
                        # Format: timestamp - level - json
                        parts = line.split(' - ', 2)
                        if len(parts) < 3:
                            continue

                        entry = json.loads(parts[2])

                        # Check timestamp filter
                        if since:
                            entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                            if entry_time < since:
                                continue

                        event_type = entry.get("event_type", "")

                        stats["total_checks"] += 1

                        if event_type == "input_check":
                            stats["input_checks"] += 1
                        elif event_type == "output_check":
                            stats["output_checks"] += 1
                        elif event_type == "tool_call":
                            stats["tool_calls"] += 1
                        elif event_type == "content_blocked":
                            stats["blocks"] += 1
                        elif event_type == "guardrail_error":
                            stats["errors"] += 1

                        # Track risk levels
                        risk = entry.get("risk_level", "none")
                        if risk in stats["risk_levels"]:
                            stats["risk_levels"][risk] += 1

                    except (json.JSONDecodeError, ValueError):
                        continue

        except Exception as e:
            stats["error"] = str(e)

        return stats


class AuditTrail:
    """
    Maintains an audit trail for compliance and debugging.

    Stores detailed records of all guardrail decisions.
    """

    def __init__(self, storage_path: str = "audit_trail"):
        """
        Initialize audit trail.

        Args:
            storage_path: Directory for audit records
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        session_id: str,
        event: Dict[str, Any]
    ):
        """
        Record an event in the audit trail.

        Args:
            session_id: Session identifier
            event: Event data to record
        """
        # Create session file
        session_file = self.storage_path / f"{session_id}.jsonl"

        record = {
            "timestamp": datetime.now().isoformat(),
            **event
        }

        with open(session_file, 'a') as f:
            f.write(json.dumps(record) + "\n")

    def get_session_trail(self, session_id: str) -> list:
        """
        Get audit trail for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of audit records
        """
        session_file = self.storage_path / f"{session_id}.jsonl"

        if not session_file.exists():
            return []

        records = []
        with open(session_file, 'r') as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return records
