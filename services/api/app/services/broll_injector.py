# services/api/app/services/broll_injector.py
"""
B-roll injection service.
SRP: Decide B-roll overlay layers based on tags and scene cuts.
"""
from __future__ import annotations

import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class BRollRule:
    """Represents a single B-roll injection rule."""

    def __init__(
        self,
        when_tag: str,
        asset_path: str,
        start_offset: float = 0.0,
        duration: float = 3.0,
        opacity: float = 1.0,
        track: int = 2,
    ):
        """
        Initialize B-roll rule.

        Args:
            when_tag: Tag that triggers this B-roll
            asset_path: Path to B-roll video asset
            start_offset: Offset from scene start (seconds)
            duration: B-roll duration (seconds)
            opacity: Opacity level (0.0-1.0)
            track: Video track number for compositing
        """
        self.when_tag = when_tag
        self.asset_path = asset_path
        self.start_offset = start_offset
        self.duration = duration
        self.opacity = opacity
        self.track = track

    def __repr__(self) -> str:
        return (
            f"BRollRule(tag={self.when_tag}, asset={self.asset_path}, "
            f"offset={self.start_offset}, duration={self.duration})"
        )


class BRollInjector:
    """
    B-roll injection engine.
    Plans additional video layers based on tags and scene cuts.
    """

    def __init__(self, rules: List[BRollRule]) -> None:
        """
        Initialize injector with rules.

        Args:
            rules: List of B-roll rules to apply
        """
        self.rules = rules
        logger.info(f"BRollInjector initialized with {len(rules)} rules")

    @staticmethod
    def from_json(spec: Dict[str, Any]) -> "BRollInjector":
        """
        Create injector from JSON specification.

        Args:
            spec: Dict with "rules" key containing list of rule dicts

        Returns:
            BRollInjector instance
        """
        rules = []
        for r in spec.get("rules", []):
            try:
                rule = BRollRule(**r)
                rules.append(rule)
            except Exception as e:
                logger.warning(f"Invalid B-roll rule: {e}")

        return BRollInjector(rules)

    def plan_layers(
        self, tags: List[str], scene_cuts: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Plan B-roll layers based on tags and scene cuts.

        Args:
            tags: List of tags associated with the video
            scene_cuts: List of scene cut timestamps (seconds)

        Returns:
            List of layer dictionaries for compositor
        """
        layers: List[Dict[str, Any]] = []
        tagset = set(tags or [])
        t0 = scene_cuts[0] if scene_cuts else 0.0

        for rule in self.rules:
            # Check if tag matches
            if rule.when_tag not in tagset:
                continue

            # Check if asset exists
            if not os.path.exists(rule.asset_path):
                logger.warning(
                    f"B-roll asset not found: {rule.asset_path} for tag {rule.when_tag}"
                )
                continue

            # Create layer specification
            layer = {
                "path": rule.asset_path,
                "track": rule.track,
                "start": max(0.0, t0 + rule.start_offset),
                "duration": rule.duration,
                "opacity": rule.opacity,
                "mode": "overlay",
            }

            layers.append(layer)
            logger.info(
                f"Added B-roll layer: tag={rule.when_tag}, asset={rule.asset_path}, "
                f"start={layer['start']:.2f}s, duration={rule.duration:.2f}s"
            )

        logger.info(f"Planned {len(layers)} B-roll layers")
        return layers
