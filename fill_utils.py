import torch
import numpy as np
from typing import List
from data.types import ObjectCandidate, PartCandidate

SPLIT_STRATEGIES = ["auto", "vertical_split", "saliency_split", "skip"]


class BGPartSplitNode:
    """
    오브젝트를 Spine 애니메이션에 유리한 파츠로 분해.
    MVP: 형태(aspect ratio) 기반 규칙으로 상하 분할.
    Phase 2: 분할 규칙 정교화, saliency_split 구현.
    """

    CATEGORY = "BG Spine Separator"
    RETURN_TYPES = ("BG_PART_CANDIDATES", "IMAGE")
    RETURN_NAMES = ("part_candidates", "part_preview")
    FUNCTION = "split"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "object_candidates": ("BG_OBJECT_CANDIDATES",),
                "split_strategy": (SPLIT_STRATEGIES, {"default": "auto"}),
                "enable_pivot_hint": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "debug_mode": ("BOOLEAN", {"default": False}),
            },
        }

    def split(self, image, object_candidates, split_strategy, enable_pivot_hint, debug_mode=False):
        img_np = (image[0].numpy() * 255).astype(np.uint8)
        all_parts: List[PartCandidate] = []

        for obj in object_candidates:
            parts = self._split_object(obj, img_np, split_strategy)
            if enable_pivot_hint:
                for p in parts:
                    p.pivot_hint = self._estimate_pivot(p)
            all_parts.extend(parts)

        if debug_mode:
            for p in all_parts:
                print(f"[BGPartSplit] {p.id} {p.name} motion={p.motion_type} pivot={p.pivot_hint}")

        from utils.debug_utils import draw_parts_preview
        preview = draw_parts_preview(img_np, all_parts)
        preview_tensor = torch.from_numpy(
            preview.astype(np.float32) / 255.0
        ).unsqueeze(0)

        return (all_parts, preview_tensor)

    def _split_object(self, obj: ObjectCandidate, img_np, strategy: str) -> List[PartCandidate]:
        if strategy == "skip":
            return [self._obj_as_part(obj)]

        x1, y1, x2, y2 = obj.bbox
        w = x2 - x1
        h = y2 - y1
        aspect = h / max(w, 1)

        if strategy == "auto":
            if aspect > 3.0:
                # 가늘고 긴 세로형 → 상하 2분할 (lamp, pole)
                return self._vertical_split(obj)
            elif aspect > 1.5:
                # 세로형 → crown/trunk 2분할 (tree)
                return self._top_bottom_split(obj, ratio=0.5)
            else:
                # 가로 또는 정방형 → 분할 없음
                return [self._obj_as_part(obj)]
        elif strategy == "vertical_split":
            return self._vertical_split(obj)
        elif strategy == "saliency_split":
            # TODO Phase 2: saliency map으로 내부 고현저 영역 분리
            return [self._obj_as_part(obj)]

        return [self._obj_as_part(obj)]

    def _vertical_split(self, obj: ObjectCandidate) -> List[PartCandidate]:
        """세로 2등분."""
        x1, y1, x2, y2 = obj.bbox
        mid_y = (y1 + y2) // 2
        mask_top = obj.mask.copy(); mask_top[mid_y:, :] = 0
        mask_bot = obj.mask.copy(); mask_bot[:mid_y, :] = 0
        return [
            PartCandidate(
                id=f"{obj.id}_part_01", parent_id=obj.id,
                name=f"{obj.name}_top", mask=mask_top,
                bbox=[x1, y1, x2, mid_y], motion_type="sway",
            ),
            PartCandidate(
                id=f"{obj.id}_part_02", parent_id=obj.id,
                name=f"{obj.name}_base", mask=mask_bot,
                bbox=[x1, mid_y, x2, y2], motion_type="static",
            ),
        ]

    def _top_bottom_split(self, obj: ObjectCandidate, ratio: float = 0.5) -> List[PartCandidate]:
        """비율 기반 상하 분할 (tree 계열: crown / trunk)."""
        x1, y1, x2, y2 = obj.bbox
        split_y = y1 + int((y2 - y1) * ratio)
        mask_top = obj.mask.copy(); mask_top[split_y:, :] = 0
        mask_bot = obj.mask.copy(); mask_bot[:split_y, :] = 0
        return [
            PartCandidate(
                id=f"{obj.id}_part_01", parent_id=obj.id,
                name=f"{obj.name}_crown", mask=mask_top,
                bbox=[x1, y1, x2, split_y], motion_type="sway",
            ),
            PartCandidate(
                id=f"{obj.id}_part_02", parent_id=obj.id,
                name=f"{obj.name}_trunk", mask=mask_bot,
                bbox=[x1, split_y, x2, y2], motion_type="static",
            ),
        ]

    def _obj_as_part(self, obj: ObjectCandidate) -> PartCandidate:
        return PartCandidate(
            id=f"{obj.id}_part_01", parent_id=obj.id,
            name=obj.name, mask=obj.mask,
            bbox=obj.bbox, category=obj.category,
            motion_type="sway",
        )

    def _estimate_pivot(self, part: PartCandidate) -> list:
        """마스크 기반 pivot 추정. 기본값: 하단 중심."""
        x1, y1, x2, y2 = part.bbox
        pivot_x = (x1 + x2) // 2
        pivot_y = y2
        return [pivot_x, pivot_y]
