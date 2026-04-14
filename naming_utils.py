import os
import json
import torch
import numpy as np
from datetime import datetime
from ..data.types import ObjectCandidate, PartCandidate
from ..utils.export_utils import save_layer_pngs, save_metadata_json, build_metadata


class BGExportPSDNode:
    """
    레이어 이미지, 마스크, JSON 메타데이터, PSD 출력.

    Phase 1: PNG + JSON export 실제 동작.
    Phase 2: PSD export 구현 (psd-tools).
      목표 PSD 구조:
        PSDImage
          └─ LayerGroup: "bg"
          │    └─ PixelLayer: "bg_filled"
          └─ LayerGroup: "obj_{name}"
               └─ PixelLayer: "source" (RGBA)
               └─ PixelLayer: "mask"
               └─ LayerGroup: "parts"
                    └─ PixelLayer: "{part_name}"
    """

    CATEGORY = "BG Spine Separator"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("export_dir", "metadata_json")
    OUTPUT_NODE = True
    FUNCTION = "export"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "filled_background": ("IMAGE",),
                "object_candidates": ("BG_OBJECT_CANDIDATES",),
                "scene_name": ("STRING", {"default": "bg_scene"}),
                "export_psd": ("BOOLEAN", {"default": False}),   # Phase 2까지 False 권장
                "export_json": ("BOOLEAN", {"default": True}),
                "export_layer_pngs": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "part_candidates": ("BG_PART_CANDIDATES",),
                "output_dir": ("STRING", {"default": ""}),
            },
        }

    def export(
        self,
        image,
        filled_background,
        object_candidates,
        scene_name,
        export_psd,
        export_json,
        export_layer_pngs,
        part_candidates=None,
        output_dir="",
    ):
        img_np = (image[0].numpy() * 255).astype(np.uint8)
        filled_np = (filled_background[0].numpy() * 255).astype(np.uint8)

        # 출력 폴더 생성
        if not output_dir:
            try:
                import folder_paths
                output_dir = folder_paths.get_output_directory()
            except ImportError:
                output_dir = os.path.join(os.path.dirname(__file__), "..", "output")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = os.path.join(output_dir, f"{scene_name}_{ts}")
        dirs = self._create_dirs(project_dir)

        parts = part_candidates or []
        metadata = build_metadata(scene_name, img_np.shape, object_candidates, parts)

        if export_layer_pngs:
            save_layer_pngs(img_np, filled_np, object_candidates, parts, dirs)

        if export_json:
            json_path = os.path.join(dirs["metadata"], "layers.json")
            save_metadata_json(metadata, json_path)
            print(f"[BGExport] JSON 저장: {json_path}")

        if export_psd:
            try:
                self._export_psd(img_np, filled_np, object_candidates, parts, dirs, scene_name)
            except ImportError:
                print("[BGExport] psd-tools 미설치. PSD export 생략.")
                print("[BGExport] 설치: pip install psd-tools")
            except NotImplementedError as e:
                print(f"[BGExport] {e}")

        print(f"[BGExport] 완료: {project_dir}")
        return (project_dir, json.dumps(metadata, indent=2, ensure_ascii=False))

    def _create_dirs(self, root: str) -> dict:
        dirs = {
            "root":     root,
            "preview":  os.path.join(root, "preview"),
            "layers":   os.path.join(root, "layers"),
            "masks":    os.path.join(root, "masks"),
            "metadata": os.path.join(root, "metadata"),
            "psd":      os.path.join(root, "psd"),
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)
        return dirs

    def _export_psd(self, img_np, filled_np, objects, parts, dirs, scene_name):
        """
        TODO Phase 2: psd-tools v1.9.x 기반 PSD 생성.
        구현 메모는 architecture.md §11 PSD Export 구현 메모 참고.
        """
        raise NotImplementedError(
            "[BGExport] PSD export는 Phase 2에서 구현 예정. "
            "현재는 export_psd=False 로 사용하세요."
        )
