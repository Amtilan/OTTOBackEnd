

from dataclasses import dataclass, field
from datetime import datetime

from core.apps.common.enum import EntityStatus
from core.apps.customers.entities.customers import CustomerEntity


@dataclass
class Pred_resultsEntity():
    id: int | None=field(default=None,kw_only=True)
    customer: CustomerEntity | EntityStatus=field(default=EntityStatus.NOT_LOADED)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = field(default=None)
    
    acne_count: int=field(default=0)
    severity: int=field(default=1)
    