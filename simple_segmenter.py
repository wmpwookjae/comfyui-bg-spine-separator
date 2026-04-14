from abc import ABC, abstractmethod
from typing import List
import numpy as np
from data.types import ObjectCandidate


class BaseSegmenter(ABC):
    """
    모든 segmentation 백엔드가 상속해야 하는 추상 클래스.
    새 백엔드를 추가할 때는 이 클래스만 상속하면 됨.
    """

    @abstractmethod
    def load_model(self, **kwargs):
        """모델 로드. 백엔드마다 다름."""
        pass

    @abstractmethod
    def segment(
        self,
        image: np.ndarray,          # H x W x 3, uint8
        prompt_hint: str = "",
        max_objects: int = 10,
        min_area_ratio: float = 0.02,
    ) -> List[ObjectCandidate]:
        """
        이미지에서 오브젝트 후보 목록을 반환.
        반드시 ObjectCandidate 리스트로 반환해야 함.
        """
        pass

    def refine_mask(self, mask: np.ndarray, image: np.ndarray) -> np.ndarray:
        """
        마스크 정제. 기본 구현 제공 (각 백엔드에서 override 가능).
        """
        from utils.mask_utils import smooth_mask, remove_small_components
        mask = smooth_mask(mask, kernel_size=5)
        mask = remove_small_components(mask, min_size=500)
        return mask
