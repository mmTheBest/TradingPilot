from dataclasses import dataclass

from tradepilot.trades.models import TradeRequest


class EmsxClient:
    def stage_order(self, request: TradeRequest) -> str:
        raise NotImplementedError

    def submit_order(self, order_id: str) -> str:
        raise NotImplementedError


@dataclass
class FakeEmsxClient(EmsxClient):
    counter: int = 0

    def stage_order(self, request: TradeRequest) -> str:
        self.counter += 1
        return f"emsx-{self.counter}"

    def submit_order(self, order_id: str) -> str:
        return f"submitted-{order_id}"
