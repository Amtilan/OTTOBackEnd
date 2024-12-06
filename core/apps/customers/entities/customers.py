

from dataclasses import dataclass, field
import datetime


@dataclass
class CustomerEntity:
    id: int | None = field(default=None, kw_only=True)
    first_name: str
    last_name: str
    email: str
    phone_number: str
    
    access_token: str
    refresh_token: str
    
    created_at: datetime.datetime