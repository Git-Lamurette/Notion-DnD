from dataclasses import dataclass
from typing import Optional, List, Dict, Union
from uuid import uuid4


@dataclass
class _magic_item:
    equipment_category: dict[str]
    index: str
    name: str
    rarity: dict
    url: str
    desc: Optional[List[str]] = None
    variant: Optional[bool] = None
    variants: Optional[List[dict]] = None

    def get_variants(self):
        return [x["name"] for x in self.variants]
