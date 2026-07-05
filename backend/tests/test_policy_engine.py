from __future__ import annotations

import unittest
from core.agents.policy.engine import PolicyEngine
from core.agents.policy.rules import PartialPolicyDecision
from core.agents.policy.schemas import EvaluationContext


class TestPolicyEngine(unittest.TestCase):
    def test_merge_decisions(self):
        engine = PolicyEngine()

        partials = [
            PartialPolicyDecision(
                allowedProviders=["openai", "groq"],
                maxBudget=0.1,
                allowStreaming=True,
                violations=["Violation 1"],
            ),
            PartialPolicyDecision(
                allowedProviders=["groq", "anthropic"],
                blockedProviders=["openai"],
                maxBudget=0.05,
                allowStreaming=False,
                violations=["Violation 2"],
            ),
        ]

        merged = engine.merge_decisions(partials, version=5)

        # Allowed providers should be the intersection: {"groq"}
        self.assertEqual(set(merged.allowedProviders), {"groq"})
        
        # Blocked providers should be union: {"openai"}
        self.assertEqual(set(merged.blockedProviders), {"openai"})
        
        # maxBudget should be minimum: 0.05
        self.assertEqual(merged.maxBudget, 0.05)
        
        # allowStreaming should be logical AND: False
        self.assertFalse(merged.allowStreaming)
        
        # violations should contain both
        self.assertEqual(merged.violations, ["Violation 1", "Violation 2"])
        self.assertEqual(merged.policyVersion, 5)

    def test_evaluate_policy_empty_rules(self):
        engine = PolicyEngine()
        context = EvaluationContext(query="Hello world")
        decision = engine.evaluate(context, {}, policy_version=1)
        self.assertEqual(decision.policyVersion, 1)
        self.assertEqual(decision.violations, [])
