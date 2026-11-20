"""
JARVIS Summarizer Service

Summarizes Discord conversations for authorized users.
Will use Gemini for actual summarization in Phase 2.
"""

from typing import Optional

from discord import TextChannel, Message

from utils.logger import get_logger

logger = get_logger("summarizer")


class SummarizerService:
    """
    Service for summarizing Discord conversations.
    Phase 1: Basic message counting and context.
    Phase 2+: Gemini-powered summarization.
    """

    def __init__(self):
        self._recent_messages: list[dict] = []

    async def gather_messages(
        self,
        channel: TextChannel,
        limit: int = 50,
        since_user_last_visit: Optional[int] = None,
    ) -> list[dict]:
        """
        Gather messages from a channel for summarization.
        Returns a list of message data.
        """
        messages = []

        try:
            async for message in channel.history(limit=limit):
                # Skip bot messages for cleaner summaries (configurable)
                if message.author.bot:
                    continue

                messages.append({
                    "id": message.id,
                    "author": message.author.name,
                    "author_id": message.author.id,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "attachments": [a.url for a in message.attachments],
                })

            logger.info(f"Gathered {len(messages)} messages from {channel.id}")
        except Exception as e:
            logger.error(f"Error gathering messages from {channel.id}: {e}")

        return messages

    def summarize_basic(self, messages: list[dict]) -> str:
        """
        Create a basic summary from messages.
        Counts messages, identifies participants, lists topics.
        """
        if not messages:
            return "No messages found to summarize."

        participants = set()
        message_count = len(messages)

        for msg in messages:
            participants.add(msg["author"])

        participant_list = ", ".join(sorted(participants))

        # Basic topic extraction (first few messages)
        topics = []
        for msg in messages[:5]:
            if msg["content"].strip():
                topics.append(msg["content"][:100])

        summary = (
            f"--- Summary ---\n"
            f"Messages analyzed: {message_count}\n"
            f"Participants: {participant_list}\n"
            f"Recent topics:\n"
        )

        for topic in topics:
            summary += f"  - {topic}\n"

        return summary

    def identify_action_items(self, messages: list[dict]) -> list[str]:
        """
        Identify potential action items from messages.
        Simple keyword-based detection for Phase 1.
        """
        action_items = []
        action_keywords = ["todo", "to-do", "task", "remind", "follow up", "need to", "must", "should"]

        for msg in messages:
            content = msg["content"].lower()
            for keyword in action_keywords:
                if keyword in content:
                    action_items.append(f"{msg['author']}: {msg['content'][:150]}")
                    break

        return action_items

    def identify_unanswered_questions(self, messages: list[dict]) -> list[str]:
        """
        Identify questions that may need answers.
        """
        questions = []
        question_endings = ["?", "？"]

        for msg in messages:
            content = msg["content"].strip()
            if content and any(content.endswith(ending) for ending in question_endings):
                # Skip questions from the last message if it might be answered
                questions.append(f"{msg['author']}: {content[:200]}")

        return questions

    def get_updates_since_last_visit(
        self,
        messages: list[dict],
        user_last_visit: Optional[str],
    ) -> list[dict]:
        """
        Filter messages to show only those since the user's last visit.
        """
        if not user_last_visit:
            return messages

        updates = []
        for msg in messages:
            if msg["timestamp"] > user_last_visit:
                updates.append(msg)

        return updates
