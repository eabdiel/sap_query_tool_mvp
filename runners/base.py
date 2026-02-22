from __future__ import annotations
from abc import ABC, abstractmethod
from models.profile import ConnectionProfile
from models.query_result import QueryResult

class QueryRunnerBase(ABC):
    def __init__(self, profile: ConnectionProfile):
        self.profile = profile

    @abstractmethod
    def run(self, sql_text: str) -> QueryResult:
        raise NotImplementedError
