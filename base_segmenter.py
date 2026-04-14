from backends.base_segmenter import BaseSegmenter
from typing import List
import numpy as np
from data.types import ObjectCandidate


class GroundedSAMSegmenter(BaseSegmenter):
    """
    TODO: Phase 3 — Grounded SAM 백엔드.
    prompt_hint 텍스트를 실제 세그멘테이션에 활용하는 첫 번째 백엔드.
    groundingdino + SAM 조합.
    """

    def load_model(self, **kwargs):
        raise NotImplementedError(
            "[GroundedSAMSegmenter] Phase 3 미구현. "
            "groundingdino-py + segment-anything 설치 후 구현 예정."
        )

    def segment(
        self,
        image: np.ndarray,
        prompt_hint: str = "",      # Phase 3: 실제로 활용됨
        max_objects: int = 10,
        min_area_ratio: float = 0.02,
    ) -> List[ObjectCandidate]:
        raise NotImplementedError("[GroundedSAMSegmenter] Phase 3 미구현.")
