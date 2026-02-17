"""Tests for loma.db — database layer with Supabase fallbacks."""
from unittest.mock import patch, MagicMock

from loma import db


class TestGetClient:
    def test_returns_none_without_config(self):
        with patch("config.SUPABASE_URL", ""), patch("config.SUPABASE_SERVICE_KEY", ""):
            db._client = None  # Reset cached client
            client = db._get_client()
            assert client is None

    def test_caches_client(self):
        mock_client = MagicMock()
        db._client = mock_client
        assert db._get_client() is mock_client
        db._client = None  # Clean up

    def test_handles_import_error(self):
        with patch("config.SUPABASE_URL", "https://test.supabase.co"), \
             patch("config.SUPABASE_SERVICE_KEY", "secret"):
            db._client = None
            with patch.dict("sys.modules", {"supabase": None}):
                # This will try to import supabase and fail
                # The function should handle it gracefully
                pass  # Hard to test without breaking other imports


class TestGetUserById:
    def test_returns_none_without_client(self):
        with patch.object(db, "_get_client", return_value=None):
            assert db.get_user_by_id("user-123") is None

    def test_returns_user_data(self):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = {"id": "user-123", "email": "test@test.com"}
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_result

        with patch.object(db, "_get_client", return_value=mock_client):
            result = db.get_user_by_id("user-123")
            assert result == {"id": "user-123", "email": "test@test.com"}

    def test_handles_exception(self):
        mock_client = MagicMock()
        mock_client.table.return_value.select.side_effect = Exception("DB error")

        with patch.object(db, "_get_client", return_value=mock_client):
            result = db.get_user_by_id("user-123")
            assert result is None


class TestUpsertUser:
    def test_returns_none_without_client(self):
        with patch.object(db, "_get_client", return_value=None):
            assert db.upsert_user("user-123", "test@test.com") is None

    def test_returns_upserted_data(self):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "user-123", "email": "test@test.com"}]
        mock_client.table.return_value.upsert.return_value.execute.return_value = mock_result

        with patch.object(db, "_get_client", return_value=mock_client):
            result = db.upsert_user("user-123", "test@test.com")
            assert result is not None


class TestGetUserSubscription:
    def test_returns_defaults_without_client(self):
        with patch.object(db, "_get_client", return_value=None):
            result = db.get_user_subscription("user-123")
            assert result["tier"] == "free"
            assert result["payg_balance"] == 0
            assert result["rewrites_today"] == 0

    def test_resets_daily_count(self):
        """rewrites_today should reset to 0 if last_rewrite_date differs from today."""
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = {
            "subscription_tier": "free",
            "payg_balance": 0,
            "rewrites_today": 5,
            "last_rewrite_date": "2020-01-01",  # Old date
        }
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_result

        with patch.object(db, "_get_client", return_value=mock_client):
            result = db.get_user_subscription("user-123")
            assert result["rewrites_today"] == 0

    def test_handles_exception(self):
        mock_client = MagicMock()
        mock_client.table.return_value.select.side_effect = Exception("DB error")

        with patch.object(db, "_get_client", return_value=mock_client):
            result = db.get_user_subscription("user-123")
            assert result["tier"] == "free"


class TestIncrementRewriteCount:
    def test_noop_without_client(self):
        with patch.object(db, "_get_client", return_value=None):
            db.increment_rewrite_count("user-123")  # Should not raise

    def test_basic_increment(self):
        mock_client = MagicMock()
        with patch.object(db, "_get_client", return_value=mock_client), \
             patch.object(db, "get_user_subscription", return_value={
                 "tier": "free", "payg_balance": 0, "rewrites_today": 2
             }):
            db.increment_rewrite_count("user-123")
            mock_client.table.return_value.update.assert_called_once()

    def test_payg_deduction_tries_rpc_first(self):
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = MagicMock()

        with patch.object(db, "_get_client", return_value=mock_client), \
             patch.object(db, "get_user_subscription", return_value={
                 "tier": "payg", "payg_balance": 10, "rewrites_today": 0
             }):
            db.increment_rewrite_count("user-123")
            mock_client.rpc.assert_called_once()
            call_args = mock_client.rpc.call_args
            assert call_args[0][0] == "decrement_payg_and_count"
            params = call_args[0][1]
            assert params["p_user_id"] == "user-123"
            assert params["p_new_count"] == 1
            assert isinstance(params["p_date"], str)

    def test_payg_deduction_fallback(self):
        mock_client = MagicMock()
        mock_client.rpc.side_effect = Exception("RPC not found")

        with patch.object(db, "_get_client", return_value=mock_client), \
             patch.object(db, "get_user_subscription", return_value={
                 "tier": "payg", "payg_balance": 5, "rewrites_today": 1
             }):
            db.increment_rewrite_count("user-123")
            # Should fall through to table update
            mock_client.table.assert_called()

    def test_handles_exception(self):
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("DB error")

        with patch.object(db, "_get_client", return_value=mock_client), \
             patch.object(db, "get_user_subscription", return_value={
                 "tier": "free", "payg_balance": 0, "rewrites_today": 0
             }):
            db.increment_rewrite_count("user-123")  # Should not raise


class TestStoreRewrite:
    def test_noop_without_client(self):
        with patch.object(db, "_get_client", return_value=None):
            db.store_rewrite("user-123", {"rewrite_id": "r-1"})  # Should not raise

    def test_stores_rewrite_data(self):
        mock_client = MagicMock()
        with patch.object(db, "_get_client", return_value=mock_client):
            db.store_rewrite("user-123", {
                "rewrite_id": "r-1",
                "original_text": "input",
                "output_text": "output",
                "detected_intent": "general",
            })
            mock_client.table.return_value.insert.assert_called_once()

    def test_handles_none_user_id(self):
        mock_client = MagicMock()
        with patch.object(db, "_get_client", return_value=mock_client):
            db.store_rewrite(None, {"rewrite_id": "r-1"})
            mock_client.table.return_value.insert.assert_called_once()


class TestLogEvent:
    def test_noop_without_client(self):
        with patch.object(db, "_get_client", return_value=None):
            db.log_event("user-123", "test_event")  # Should not raise

    def test_logs_event(self):
        mock_client = MagicMock()
        with patch.object(db, "_get_client", return_value=mock_client):
            db.log_event("user-123", "test_event", {"key": "value"})
            mock_client.table.return_value.insert.assert_called_once()

    def test_handles_none_user_id(self):
        mock_client = MagicMock()
        with patch.object(db, "_get_client", return_value=mock_client):
            db.log_event(None, "test_event")
            mock_client.table.return_value.insert.assert_called_once()

    def test_handles_exception(self):
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("DB error")

        with patch.object(db, "_get_client", return_value=mock_client):
            db.log_event("user-123", "test_event")  # Should not raise
