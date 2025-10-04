from __future__ import annotations
import json, hashlib
from pathlib import Path
from typing import Dict, Any

class ContentStorage:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "assets").mkdir(exist_ok=True)
        (self.storage_path / "thumbnails").mkdir(exist_ok=True)

    def save_content_data(self, content_data: Dict[str, Any]) -> None:
        f = self.storage_path / "content_data.json"
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(content_data, fh, indent=2, ensure_ascii=False, default=str)

    def load_content_data(self) -> Dict[str, Any]:
        f = self.storage_path / "content_data.json"
        if not f.exists():
            return {"content_items": {}, "assets": {}}
        with open(f, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def generate_content_id(self, title: str) -> str:
        return "content_" + hashlib.md5(title.encode()).hexdigest()[:12]

    def generate_asset_id(self, asset_path: str) -> str:
        return "asset_" + hashlib.md5(asset_path.encode()).hexdigest()[:12]
