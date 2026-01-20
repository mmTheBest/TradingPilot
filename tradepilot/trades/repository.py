from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.db.models.tradeflow import StagedTradeRecord, TradeApproval, TradeSubmitQueue


@dataclass
class TradeRepository:
    session_factory: Callable[[], Session]

    def create_staged_trade(
        self,
        tenant_id: str,
        book_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        limit_price: Optional[float],
        status: str,
        emsx_order_id: Optional[str],
        positions_as_of_ts: str,
        limits_version_id: str,
        fx_rate_snapshot_id: Optional[str],
    ) -> str:
        trade_id = str(uuid4())
        created_at = datetime.now(tz=timezone.utc).isoformat()
        record = StagedTradeRecord(
            trade_id=trade_id,
            tenant_id=tenant_id,
            book_id=book_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price,
            status=status,
            emsx_order_id=emsx_order_id,
            positions_as_of_ts=positions_as_of_ts,
            limits_version_id=limits_version_id,
            fx_rate_snapshot_id=fx_rate_snapshot_id,
            created_at=created_at,
        )
        with self.session_factory() as session:
            session.add(record)
            session.commit()
        return trade_id

    def record_approval(
        self,
        trade_id: str,
        action: str,
        reason: Optional[str],
        slack_user_id: str,
        approver_id: Optional[str],
        approver_effective_from: Optional[str],
        approver_effective_to: Optional[str],
    ) -> None:
        approval = TradeApproval(
            id=str(uuid4()),
            trade_id=trade_id,
            action=action,
            reason=reason,
            slack_user_id=slack_user_id,
            approver_id=approver_id,
            approver_effective_from=approver_effective_from,
            approver_effective_to=approver_effective_to,
            created_at=datetime.now(tz=timezone.utc).isoformat(),
        )
        with self.session_factory() as session:
            session.add(approval)
            session.commit()

    def update_trade_status(self, trade_id: str, status: str) -> None:
        with self.session_factory() as session:
            record = session.get(StagedTradeRecord, trade_id)
            if record is None:
                raise ValueError("trade not found")
            record.status = status
            session.commit()

    def get_trade(self, trade_id: str) -> Optional[StagedTradeRecord]:
        with self.session_factory() as session:
            return session.get(StagedTradeRecord, trade_id)

    def enqueue_submission(self, trade_id: str, next_attempt_at: str) -> None:
        now = datetime.now(tz=timezone.utc).isoformat()
        item = TradeSubmitQueue(
            id=str(uuid4()),
            trade_id=trade_id,
            status="pending",
            attempts=0,
            next_attempt_at=next_attempt_at,
            last_error=None,
            created_at=now,
            updated_at=now,
        )
        with self.session_factory() as session:
            session.add(item)
            session.commit()
