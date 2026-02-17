"""Tests for loma.analytics — event tracking, acceptance rates, user edit tracking."""
from unittest.mock import patch, MagicMock

from loma import analytics
from loma.analytics import (
    track,
    track_rewrite,
    track_user_edit,
    compute_acceptance_rates,
    EVENT_REWRITE,
    EVENT_USE,
    EVENT_USER_EDIT,
    EVENT_QUOTA_HIT,
    EVENT_ERROR,
)


class TestEventConstants:
    def test_event_names_are_strings(self):
        assert isinstance(EVENT_REWRITE, str)
        assert isinstance(EVENT_USE, str)
        assert isinstance(EVENT_USER_EDIT, str)
        assert isinstance(EVENT_QUOTA_HIT, str)
        assert isinstance(EVENT_ERROR, str)

    def test_event_names_have_loma_prefix(self):
        assert EVENT_REWRITE.startswith("loma_")
        assert EVENT_USE.startswith("loma_")
        assert EVENT_USER_EDIT.startswith("loma_")
        assert EVENT_QUOTA_HIT.startswith("loma_")
        assert EVENT_ERROR.startswith("loma_")


class TestTrack:
    @patch("loma.analytics.db")
    def test_calls_log_event(self, mock_db):
        track("test_event", user_id="user-1", properties={"key": "val"})
        mock_db.log_event.assert_called_once_with(
            user_id="user-1",
            event_name="test_event",
            event_data={"key": "val"},
        )

    @patch("loma.analytics.db")
    def test_handles_none_properties(self, mock_db):
        track("test_event", user_id="user-1")
        mock_db.log_event.assert_called_once_with(
            user_id="user-1",
            event_name="test_event",
            event_data=None,
        )

    @patch("loma.analytics.db")
    def test_handles_exception_silently(self, mock_db):
        mock_db.log_event.side_effect = Exception("DB error")
        track("test_event")  # Should not raise

    @patch("loma.analytics.db")
    def test_none_user_id(self, mock_db):
        track("test_event", user_id=None)
        mock_db.log_event.assert_called_once()


class TestTrackRewrite:
    @patch("loma.analytics.db")
    def test_tracks_rewrite_with_standard_props(self, mock_db):
        result = {
            "rewrite_id": "r-1",
            "detected_intent": "follow_up",
            "routing_tier": "haiku",
            "output_language": "en",
            "response_time_ms": 250,
            "language_mix": {"vi_ratio": 0.5},
            "scores": {"entity_preserved_pct": 100},
        }
        track_rewrite("user-1", result)
        mock_db.log_event.assert_called_once()
        call_args = mock_db.log_event.call_args
        assert call_args.kwargs["event_name"] == EVENT_REWRITE
        event_data = call_args.kwargs["event_data"]
        assert event_data["rewrite_id"] == "r-1"
        assert event_data["detected_intent"] == "follow_up"


class TestTrackUserEdit:
    @patch("loma.analytics.db")
    def test_tracks_edit(self, mock_db):
        track_user_edit(
            user_id="user-1",
            rewrite_id="r-1",
            original_output="Hello, please review.",
            edited_output="Hi, please review this document.",
            detected_intent="follow_up",
            platform="gmail",
        )
        mock_db.log_event.assert_called_once()
        call_args = mock_db.log_event.call_args
        event_data = call_args.kwargs["event_data"]
        assert event_data["rewrite_id"] == "r-1"
        assert event_data["detected_intent"] == "follow_up"
        assert event_data["platform"] == "gmail"
        assert "edit_distance_pct" in event_data

    @patch("loma.analytics.db")
    def test_skips_empty_original(self, mock_db):
        track_user_edit("user-1", "r-1", "", "new text", "general")
        mock_db.log_event.assert_not_called()

    @patch("loma.analytics.db")
    def test_skips_empty_edited(self, mock_db):
        track_user_edit("user-1", "r-1", "old text", "", "general")
        mock_db.log_event.assert_not_called()

    @patch("loma.analytics.db")
    def test_skips_identical_text(self, mock_db):
        track_user_edit("user-1", "r-1", "same text", "same text", "general")
        mock_db.log_event.assert_not_called()

    @patch("loma.analytics.db")
    def test_edit_distance_calculation(self, mock_db):
        track_user_edit(
            user_id="user-1",
            rewrite_id="r-1",
            original_output="word1 word2 word3",
            edited_output="word1 word4 word3",
            detected_intent="general",
        )
        call_args = mock_db.log_event.call_args
        event_data = call_args.kwargs["event_data"]
        assert event_data["words_added"] == 1
        assert event_data["words_removed"] == 1


class TestComputeAcceptanceRates:
    @patch("loma.analytics.db")
    def test_returns_none_without_client(self, mock_db):
        mock_db._get_client.return_value = None
        result = compute_acceptance_rates()
        assert result is None

    @patch("loma.analytics.db")
    def test_computes_rates(self, mock_db):
        mock_client = MagicMock()
        mock_db._get_client.return_value = mock_client

        # Mock rewrite events
        rewrite_result = MagicMock()
        rewrite_result.data = [
            {"event_data": {"detected_intent": "follow_up"}},
            {"event_data": {"detected_intent": "follow_up"}},
            {"event_data": {"detected_intent": "say_no"}},
        ]
        # Mock use events
        use_result = MagicMock()
        use_result.data = [
            {"event_data": {"detected_intent": "follow_up"}},
        ]

        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.side_effect = [
            rewrite_result,
            use_result,
        ]

        result = compute_acceptance_rates()
        assert result is not None
        assert result["total_rewrites"] == 3
        assert result["total_uses"] == 1
        assert result["overall_rate"] == round(1 / 3, 3)
        assert "follow_up" in result["by_intent"]

    @patch("loma.analytics.db")
    def test_handles_exception(self, mock_db):
        mock_client = MagicMock()
        mock_db._get_client.return_value = mock_client
        mock_client.table.side_effect = Exception("DB error")

        result = compute_acceptance_rates()
        assert result is None
