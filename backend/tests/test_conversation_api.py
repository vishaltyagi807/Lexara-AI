from __future__ import annotations

import unittest
import uuid
from fastapi.testclient import TestClient
from app.main import app


class TestConversationAPI(unittest.TestCase):
    def setUp(self):
        import os
        os.environ["TESTING"] = "1"
        self.client = TestClient(app)
        self.conversation_id = str(uuid.uuid4())

    def tearDown(self):
        import asyncio
        from app.api.v1.chat.chat import _conv_service
        from app.db.session import engine
        try:
            loop = asyncio.get_event_loop()
            tasks = [engine.dispose()]
            if _conv_service._background_tasks:
                tasks.extend(list(_conv_service._background_tasks))
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        except Exception:
            pass

    def _await_background_tasks(self):
        import asyncio
        from app.api.v1.chat.chat import _conv_service
        if _conv_service._background_tasks:
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(asyncio.gather(*list(_conv_service._background_tasks), return_exceptions=True))
            except Exception:
                pass

    def test_chat_and_management_flow(self):
        # 1. POST /api/v1/chat/ (create interaction)
        chat_req = {
            "message": "Verify conversation persistence",
            "conversation_id": self.conversation_id,
            "user_id": str(uuid.uuid4()),
        }
        res = self.client.post("/api/v1/chat/", json=chat_req)
        self._await_background_tasks()
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["conversation_id"], self.conversation_id)
        self.assertIsNotNone(data["response"])

        # 2. GET /api/v1/chat/{conversation_id} (fetch history)
        res_get = self.client.get(f"/api/v1/chat/{self.conversation_id}")
        self.assertEqual(res_get.status_code, 200)
        hist_data = res_get.json()
        self.assertEqual(hist_data["id"], self.conversation_id)
        # Should contain at least 2 messages (user query + assistant response)
        self.assertGreaterEqual(len(hist_data["messages"]), 2)

        # 3. PUT /api/v1/chat/{conversation_id} (rename)
        res_rename = self.client.put(f"/api/v1/chat/{self.conversation_id}?title=CustomTitle")
        self.assertEqual(res_rename.status_code, 200)
        self.assertEqual(res_rename.json()["status"], "ok")

        # Verify rename
        res_get_updated = self.client.get(f"/api/v1/chat/{self.conversation_id}")
        self.assertEqual(res_get_updated.json()["title"], "CustomTitle")

        # 4. GET /api/v1/chat/{conversation_id}/export (export)
        res_export = self.client.get(f"/api/v1/chat/{self.conversation_id}/export")
        self.assertEqual(res_export.status_code, 200)
        export_data = res_export.json()
        self.assertEqual(export_data["conversation_id"], self.conversation_id)
        self.assertEqual(export_data["title"], "CustomTitle")
        self.assertGreaterEqual(len(export_data["history"]), 2)

        # 5. DELETE /api/v1/chat/{conversation_id} (soft delete)
        res_delete = self.client.delete(f"/api/v1/chat/{self.conversation_id}")
        self.assertEqual(res_delete.status_code, 200)
        self.assertEqual(res_delete.json()["status"], "ok")
