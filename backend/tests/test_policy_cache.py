from __future__ import annotations

import unittest
from datetime import datetime
from core.agents.policy.cache import PolicyCache


class TestPolicyCache(unittest.TestCase):
    def setUp(self):
        self.cache = PolicyCache()
        self.cache.clear()

    def test_singleton_behavior(self):
        cache2 = PolicyCache()
        self.assertIs(self.cache, cache2)

    def test_get_set_policy(self):
        self.assertIsNone(self.cache.get_active_policy())
        self.assertIsNone(self.cache.current_version())

        rules = {"provider": {"allowed_providers": ["openai"]}}
        self.cache.set_policy(1, rules)

        self.assertEqual(self.cache.get_active_policy(), rules)
        self.assertEqual(self.cache.current_version(), 1)
        self.assertIsInstance(self.cache.last_updated(), datetime)

    def test_stats(self):
        rules = {"provider": {"allowed_providers": ["openai"]}}
        self.cache.set_policy(2, rules)
        
        # Access cache to increment hits/misses
        _ = self.cache.get_active_policy()
        _ = self.cache.get_active_policy()
        
        stats = self.cache.get_stats()
        self.assertEqual(stats["version"], 2)
        self.assertEqual(stats["reload_count"], 1)
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 0)
