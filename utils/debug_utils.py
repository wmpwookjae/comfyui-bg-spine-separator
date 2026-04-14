import cv2
import numpy as np
from typing import List


def draw_candidates_preview(img_np: np.ndarray, candidates: list) -> np.ndarray:
    """오브젝트 후보를 컬러 오버레이로 시각화."""
    preview = img_np.copy()
    colors = [
        (255, 100, 100), (100, 255, 100), (100, 100, 255),
        (255, 255, 100), (255, 100, 255), (100, 255, 255),
        (200, 150, 50),  (50, 200, 150),  (150, 50, 200),
    ]
    for i, c in enumerate(candidates):
        color = colors[i % len(colors)]
        overlay = preview.copy()
        overlay[c.mask > 0.5] = color
        preview = cv2.addWeighted(overlay, 0.4, preview, 0.6, 0)
        x1, y1, x2, y2 = c.bbox
        cv2.rectangle(preview, (x1, y1), (x2, y2), color, 2)
        cv2.putText(preview, c.name, (x1, max(y1 - 5, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return preview


def draw_parts_preview(img_np: np.ndarray, parts: list) -> np.ndarray:
    """파츠를 오버레이로 시각화 + pivot 점 표시."""
    preview = img_np.copy()
    for p in parts:
        overlay = preview.copy()
        overlay[p.mask > 0.5] = (200, 150, 50)
        preview = cv2.addWeighted(overlay, 0.35, preview, 0.65, 0)
        if p.pivot_hint:
            cv2.circle(preview, tuple(p.pivot_hint), 5, (255, 0, 0), -1)
    return preview


def make_hole_fill_debug(original: np.ndarray, mask: np.ndarray, filled: np.ndarray) -> np.ndarray:
    """원본 / 마스크 / 결과 3분할 프리뷰."""
    h, w = original.shape[:2]
    third_w = w // 3
    third_h = h // 3
    mask_vis = np.stack([mask * 255] * 3, axis=-1).astype(np.uint8)
    row = np.concatenate([
        cv2.resize(original, (third_w, third_h)),
        cv2.resize(mask_vis, (third_w, third_h)),
        cv2.resize(filled, (third_w, third_h)),
    ], axis=1)
    return row
