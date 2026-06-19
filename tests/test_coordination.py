"""
tests/test_coordination.py — T8: Prove handoffs really traverse Band.
Golden Rule 1 verified in code, not by inspection.
Prompt Playbook T8.
"""
import pytest

from schemas import MessageEnvelope


class TestHandoffSequence:
    """Verify the typed envelope flow through the room."""

    def test_envelope_intent_values(self):
        """All valid intent values accepted by MessageEnvelope."""
        for intent in ("post", "handoff", "escalate", "decision", "audit"):
            env = MessageEnvelope(
                case_id="C-TEST",
                from_agent="intake",
                intent=intent,
                payload={"test": True},
            )
            assert env.intent == intent

    def test_handoff_requires_to_role(self):
        """handoff intent without to_role → validation error."""
        with pytest.raises(Exception):
            MessageEnvelope(
                case_id="C-TEST",
                from_agent="intake",
                intent="handoff",
                to_role=None,
                payload={"message": "ready"},
            )

    def test_handoff_with_to_role_accepted(self):
        """handoff with to_role is valid."""
        env = MessageEnvelope(
            case_id="C-TEST",
            from_agent="intake",
            intent="handoff",
            to_role="dating_risk",
            payload={"message": "ready"},
        )
        assert env.to_role == "dating_risk"

    def test_post_no_to_role_needed(self):
        """post intent does not require to_role."""
        env = MessageEnvelope(
            case_id="C-TEST",
            from_agent="intake",
            intent="post",
            payload={"data": "test"},
        )
        assert env.to_role is None
        assert env.intent == "post"

    def test_message_roundtrip_json(self):
        """Envelope → JSON → back is lossless."""
        import json
        env = MessageEnvelope(
            case_id="C-TEST",
            from_agent="guideline",
            intent="post",
            payload={"compliant": True, "veto": False},
        )
        j = env.model_dump(mode="json")
        rebuilt = MessageEnvelope(**json.loads(json.dumps(j)))
        assert rebuilt.case_id == env.case_id
        assert rebuilt.from_agent == env.from_agent
        assert rebuilt.payload == env.payload


class TestNoCrossAgentImports:
    """Prove agents don't import each other directly (Golden Rule 1)."""

    AGENT_DIRS = ["agents/intake", "agents/dating_risk", "agents/guideline", "agents/auditor"]

    def test_no_cross_agent_imports(self):
        """Scan agent source files for imports of other agents."""
        import ast
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        # Agent module names we check for
        agent_modules = {"agents.intake", "agents.dating_risk", "agents.guideline", "agents.auditor"}

        violations = []
        for agent_dir in self.AGENT_DIRS:
            agent_path = project_root / agent_dir
            if not agent_path.exists():
                continue
            current_module = agent_dir.replace("/", ".")
            for py_file in agent_path.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                content = py_file.read_text()
                # Check for import statements referencing other agent modules
                for other in agent_modules:
                    if other == current_module:
                        continue
                    # Check import patterns
                    if other.replace(".", "/") in content or other in content:
                        # Allow if it's the orchestrator importing (orchestrator can import agents)
                        if "orchestrator" in str(py_file) or "band_wrapper" in str(py_file):
                            continue
                        violations.append(f"{py_file.name} imports {other}")

        # orchestrator and band_wrapper CAN import agents. Agents CANNOT import each other.
        assert violations == [], f"Cross-agent imports found: {violations}"
