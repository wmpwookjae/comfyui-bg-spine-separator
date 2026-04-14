import os
import json
import numpy as np
from PIL import Image
from ..data.types import ObjectCandidate, PartCandidate
from .naming_utils import make_layer_filename, make_part_filename


def _to_python(obj):
    """numpy 타입을 Python 기본 타입으로 재귀 변환. JSON 직렬화 호환."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, list):
        return [_to_python(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_python(v) for k, v in obj.items()}
    return obj


def save_layer_pngs(
    img_np: np.ndarray,
    filled_np: np.ndarray,
    objects: list,
    parts: list,
    dirs: dict,
) -> None:
    """오브젝트/파츠 레이어 PNG 저장."""
    Image.fromarray(filled_np).save(os.path.join(dirs["layers"], "bg_filled.png"))

    for obj in objects:
        rgba = np.dstack([img_np, (obj.mask * 255).astype(np.uint8)])
        fname = make_layer_filename(obj.id, obj.name)
        Image.fromarray(rgba.astype(np.uint8), "RGBA").save(
            os.path.join(dirs["layers"], fname)
        )
        mask_fname = make_layer_filename(obj.id, obj.name, suffix="mask")
        Image.fromarray((obj.mask * 255).astype(np.uint8)).save(
            os.path.join(dirs["masks"], mask_fname)
        )

    for part in parts:
        rgba = np.dstack([img_np, (part.mask * 255).astype(np.uint8)])
        fname = make_part_filename(part.id, part.name)
        Image.fromarray(rgba.astype(np.uint8), "RGBA").save(
            os.path.join(dirs["layers"], fname)
        )


def save_metadata_json(metadata: dict, path: str) -> None:
    # _to_python으로 numpy 타입 전부 변환 후 저장
    clean = _to_python(metadata)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)


def build_metadata(scene_name: str, shape: tuple, objects: list, parts: list) -> dict:
    h, w = shape[:2]
    obj_dicts = []
    for obj in objects:
        obj_dicts.append({
            "id": str(obj.id),
            "name": str(obj.name),
            "type": "object",
            "depth_order": int(obj.depth_order),
            "bbox": [int(v) for v in obj.bbox],          # numpy intc → int 변환
            "category": str(obj.category),
            "area_ratio": round(float(obj.area_ratio), 4),
            "is_animatable": bool(obj.is_animatable),
            "file": f"layers/{obj.id}_{obj.name}.png",
            "mask_file": f"masks/{obj.id}_{obj.name}_mask.png",
            "parts": [
                {
                    "id": str(p.id),
                    "name": str(p.name),
                    "motion_type": str(p.motion_type),
                    "pivot_hint": [int(v) for v in p.pivot_hint] if p.pivot_hint else None,
                    "file": f"layers/{p.id}_{p.name}.png",
                }
                for p in parts if p.parent_id == obj.id
            ],
        })

    return {
        "scene_name": str(scene_name),
        "canvas_width": int(w),
        "canvas_height": int(h),
        "export_version": "1.0",
        "depth_sorted_ids": [
            o["id"] for o in sorted(obj_dicts, key=lambda x: x["depth_order"])
        ],
        "layers": obj_dicts,
        "notes": [],
    }
