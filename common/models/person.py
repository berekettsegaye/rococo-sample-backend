from rococo.models import Person as BasePerson
from typing import ClassVar, Optional
from dataclasses import dataclass


@dataclass(repr=False)
class Person(BasePerson):
    use_type_checking: ClassVar[bool] = True

    # 2FA fields
    totp_secret: Optional[str] = None
    is_2fa_enabled: bool = False
