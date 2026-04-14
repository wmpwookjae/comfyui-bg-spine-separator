import torch
import numpy as np
from data.types import SceneFeatures


class BGSceneAnalyzeNode:
    """
    배경 이미지를 분석해 오브젝트 후보 영역과 장면 특성을 반환.

    Phase 1 (MVP):
      - edge density 계산만 실제 동작.
      - region_proposals: 빈 리스트 반환 (BGObjectSegment에 실질 영향 없음).
      - prompt_hint: analysis_notes에 기록만 하고 세그멘테이션에 미반영.
      - depth_map: None 반환 → BGObjectSegment가 면적 역순으로 폴백 정렬.

    Phase 2:
      - connected components 기반 region_proposals 실제 구현.
      - dominant color clustering (k-means) 구현.
      - depth 모델 연동 (Marigold 또는 ZoeDepth).

    Phase 3:
      - CLIP/BLIP으로 prompt_hint 기반 영역 추정.
    """

    CATEGORY = "BG Spine Separator"
    RETURN_TYPES = ("BG_SCENE_FEATURES",)
    RETURN_NAMES = ("scene_features",)
    FUNCTION = "analyze"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "prompt_hint": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "e.g. fantasy hotel, trees, lamp, clouds",
                }),
                "debug_mode": ("BOOLEAN", {"default": False}),
            },
        }

    def analyze(self, image: torch.Tensor, prompt_hint: str = "", debug_mode: bool = False):
        img_np = (image[0].numpy() * 255).astype(np.uint8)
        scene = self._run_analysis(img_np, prompt_hint)
        if debug_mode:
            print(f"[BGSceneAnalyze] edge_density={scene.edge_density:.4f}")
            print(f"[BGSceneAnalyze] notes={scene.analysis_notes}")
        return (scene,)

    def _run_analysis(self, img_np: np.ndarray, prompt_hint: str) -> SceneFeatures:
        import cv2
        h, w = img_np.shape[:2]

        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = float(edges.sum()) / (h * w * 255)

        notes = []
        if prompt_hint:
            notes.append(f"prompt_hint: {prompt_hint} (Phase 1: 기록만, 미반영)")
        else:
            notes.append("prompt_hint: 없음")
        notes.append("region_proposals: Phase 2에서 구현 예정")

        return SceneFeatures(
            canvas_size=[w, h],
            edge_density=edge_density,
            dominant_colors=[],         # TODO Phase 2: k-means color clustering
            region_proposals=[],        # TODO Phase 2: connected components 기반
            depth_map=None,             # TODO Phase 2: Marigold / ZoeDepth
            analysis_notes=notes,
        )
