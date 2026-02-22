from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class QueryResult:
    columns: List[str]
    rows: List[List[Any]]
    message: str = ""
    runtime_ms: Optional[int] = None
    rowcount: Optional[int] = None
