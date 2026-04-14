import cv2
import numpy as np


def fast_inpaint(img_np: np.ndarray, mask: np.ndarray, radius: int = 15) -> np.ndarray:
    """
    OpenCV TELEA 알고리즘 기반 빠른 hole fill.
    edge 보존 양호. AI fill 대비 속도 우선.
    """
    mask_uint8 = (mask > 0.5).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_dilated = cv2.dilate(mask_uint8, kernel, iterations=2)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    filled_bgr = cv2.inpaint(img_bgr, mask_dilated, radius, cv2.INPAINT_TELEA)
    return cv2.cvtColor(filled_bgr, cv2.COLOR_BGR2RGB)
