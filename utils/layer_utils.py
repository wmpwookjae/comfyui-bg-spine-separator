import numpy as np
from ..data.types import ObjectCandidate


def extract_layer_rgba(img_np: np.ndarray, obj: ObjectCandidate) -> np.ndarray:
    """이미지에서 오브젝트 마스크를 알파채널로 적용해 RGBA 반환."""
    alpha = (obj.mask * 255).astype(np.uint8)
    return np.dstack([img_np, alpha])
