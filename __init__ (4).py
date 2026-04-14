import torch
import numpy as np
from typing import List
from data.types import ObjectCandidate, SceneFeatures

BACKEND_OPTIONS = ["simple", "sam", "grounded_sam"]


class BGObjectSegmentNode:
    """
    배경에서 움직일 가치가 있는 오브젝트를 마스크로 분리.
    segmentation backend를 플러그형으로 교체 가능.

    Phase 1: simple backend (saliency + connected components).
    Phase 2: SAM backend 연동.
    Phase 3: Grounded SAM backend 연동 (prompt_hint 실제 활용).
    """

    CATEGORY = "BG Spine Separator"
    RETURN_TYPES = ("BG_OBJECT_CANDIDATES", "IMAGE")
    RETURN_NAMES = ("object_candidates", "mask_preview")
    FUNCTION = "segment"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "segmentation_backend": (BACKEND_OPTIONS, {"default": "simple"}),
                "max_objects": ("INT", {"default": 8, "min": 1, "max": 20}),
                "min_area_ratio": ("FLOAT", {
                    "default": 0.02, "min": 0.001, "max": 0.5, "step": 0.001
                }),
                "mask_smoothness": ("INT", {"default": 5, "min": 1, "max": 15}),
            },
            "optional": {
                "scene_features": ("BG_SCENE_FEATURES",),
                "prompt_hint": ("STRING", {"default": ""}),
                "debug_mode": ("BOOLEAN", {"default": False}),
            },
        }

    def segment(
        self,
        image: torch.Tensor,
        segmentation_backend: str,
        max_objects: int,
        min_area_ratio: float,
        mask_smoothness: int,
        scene_features=None,
        prompt_hint: str = "",
        debug_mode: bool = False,
    ):
        img_np = (image[0].numpy() * 255).astype(np.uint8)

        segmenter = self._load_backend(segmentation_backend)
        candidates: List[ObjectCandidate] = segmenter.segment(
            img_np,
            prompt_hint=prompt_hint,
            max_objects=max_objects,
            min_area_ratio=min_area_ratio,
        )

        # 마스크 정제
        for c in candidates:
            c.mask = segmenter.refine_mask(c.mask, img_np)

        # depth 정렬: depth_map 있으면 사용, 없으면 면적 역순 폴백
        if scene_features and scene_features.depth_map is not None:
            candidates = self._sort_by_depth(candidates, scene_features.depth_map)
        else:
            candidates = self._sort_by_area(candidates)

        if debug_mode:
            for c in candidates:
                print(f"[BGObjectSegment] {c.id} {c.name} area={c.area_ratio:.3f} score={c.score:.3f}")

        # preview 생성
        from utils.debug_utils import draw_candidates_preview
        preview = draw_candidates_preview(img_np, candidates)
        preview_tensor = torch.from_numpy(
            preview.astype(np.float32) / 255.0
        ).unsqueeze(0)

        return (candidates, preview_tensor)

    def _load_backend(self, name: str):
        if name == "simple":
            from backends.simple_segmenter import SimpleSegmenter
            s = SimpleSegmenter()
            s.load_model()
            return s
        elif name == "sam":
            from backends.sam_segmenter import SAMSegmenter
            s = SAMSegmenter()
            s.load_model()
            return s
        elif name == "grounded_sam":
            from backends.grounded_sam_segmenter import GroundedSAMSegmenter
            s = GroundedSAMSegmenter()
            s.load_model()
            return s
        else:
            raise ValueError(f"[BGObjectSegment] 알 수 없는 backend: {name}")

    def _sort_by_depth(self, candidates, depth_map):
        for c in candidates:
            masked_depth = depth_map[c.mask > 0.5]
            c.depth_order = int(masked_depth.mean() * 100) if len(masked_depth) > 0 else 50
        return sorted(candidates, key=lambda c: c.depth_order)

    def _sort_by_area(self, candidates):
        # depth 없으면 면적 역순 (큰 것이 후경 경향)
        return sorted(candidates, key=lambda c: -c.area_ratio)
