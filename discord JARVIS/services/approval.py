"""
JARVIS Approval Service

Manages the approval workflow for consequential actions.
Actions like sending messages, moderation, and settings changes require approval.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from utils.logger import get_logger

logger = get_logger("approval")


@dataclass
class PendingApproval:
    """A pending approval request."""

    approval_id: int
    user_id: int
    action_type: str
    action_data: dict
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_resolved: bool = False


class ApprovalService:
    """
    Service for managing approval requests.
    Implements the draft → approve/reject workflow.
    """

    def __init__(self):
        self._pending: dict[int, PendingApproval] = {}
        self._next_id: int = 1

    def create_approval_request(
        self,
        user_id: int,
        action_type: str,
        action_data: dict,
        expires_in_minutes: int = 15,
    ) -> PendingApproval:
        """
        Create a new approval request.
        Returns the pending approval.
        """
        now = datetime.now()
        expires_at = now + timedelta(minutes=expires_in_minutes) if expires_in_minutes > 0 else None

        approval = PendingApproval(
            approval_id=self._next_id,
            user_id=user_id,
            action_type=action_type,
            action_data=action_data,
            created_at=now,
            expires_at=expires_at,
        )
        self._pending[self._next_id] = approval
        self._next_id += 1

        logger.info(f"Created approval request #{approval.approval_id} for user {user_id}")
        return approval

    def get_pending_approvals(self, user_id: int) -> list[PendingApproval]:
        """Get all pending approvals for a user."""
        return [
            a for a in self._pending.values()
            if a.user_id == user_id and not a.is_resolved
        ]

    def get_approval(self, approval_id: int) -> Optional[PendingApproval]:
        """Get a specific approval by ID."""
        return self._pending.get(approval_id)

    async def approve(self, approval_id: int, approver_id: int) -> tuple[bool, Optional[dict]]:
        """
        Approve an action.
        Returns (success, action_data).
        """
        approval = self.get_approval(approval_id)
        if not approval:
            logger.warning(f"Approval #{approval_id} not found")
            return False, None

        if approval.is_resolved:
            logger.warning(f"Approval #{approval_id} already resolved")
            return False, None

        if approver_id != approval.user_id:
            logger.warning(f"User {approver_id} tried to approve #{approval_id} owned by {approval.user_id}")
            return False, None

        # Check expiration
        if approval.expires_at and datetime.now() > approval.expires_at:
            logger.info(f"Approval #{approval_id} expired")
            return False, None

        approval.is_resolved = True
        logger.info(f"Approval #{approval_id} approved by user {approver_id}")

        return True, approval.action_data

    async def reject(self, approval_id: int, approver_id: int) -> bool:
        """
        Reject an action.
        Returns True if rejected successfully.
        """
        approval = self.get_approval(approval_id)
        if not approval:
            return False

        if approval.is_resolved:
            return False

        if approver_id != approval.user_id:
            return False

        approval.is_resolved = True
        logger.info(f"Approval #{approval_id} rejected by user {approver_id}")
        return True

    def get_actions_for_display(self, approval: PendingApproval) -> dict:
        """Get approval data formatted for display."""
        return {
            "id": approval.approval_id,
            "action_type": approval.action_type,
            "action_data": approval.action_data,
            "created_at": approval.created_at.isoformat(),
            "expires_at": approval.expires_at.isoformat() if approval.expires_at else None,
        }

    def clear_expired(self) -> int:
        """Clear expired approvals. Returns count of cleared approvals."""
        now = datetime.now()
        expired_ids = [
            aid for aid, a in self._pending.items()
            if not a.is_resolved and a.expires_at and now > a.expires_at
        ]
        for aid in expired_ids:
            del self._pending[aid]
        if expired_ids:
            logger.info(f"Cleared {len(expired_ids)} expired approvals")
        return len(expired_ids)
