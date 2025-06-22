from abc import ABC, abstractmethod

from indexer.app.common.ctx import Context


class BaseTracker(ABC):
    RETRY_DELAY: int = 3
    ctx: Context

    def __init__(self, ctx: Context):
        self.ctx = ctx

    @abstractmethod
    async def run(self) -> None:
        pass
