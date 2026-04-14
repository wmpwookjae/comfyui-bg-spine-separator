from .base_segmenter import BaseSegmenter
from typing import List
import numpy as np
from ..data.types import ObjectCandidate


class SAMSegmenter(BaseSegmenter):
    """
    TODO: Phase 2 — SAM (Segment Anything Model) 백엔드.
    point-based segmentation. prompt_hint 미지원.
    """

    def load_model(self, **kwargs):
        raise NotImplementedError(
            "[SAMSegmenter] Phase 2 미구현. "
            "segment-anything 설치 후 구현 예정."
        )

    def segment(
        self,
        image: np.ndarray,
        prompt_hint: str = "",
        max_objects: int = 10,
        min_area_ratio: float = 0.02,
    ) -> List[ObjectCandidate]:
        raise NotImplementedError("[SAMSegmenter] Phase 2 미구현.")
