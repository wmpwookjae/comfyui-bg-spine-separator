from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class ObjectCandidate:
    """분리된 배경 오브젝트 하나를 표현."""
    id: str                         # "obj_001"
    name: str                       # "object_01" → Phase 2에서 의미있는 이름으로 개선
    bbox: list                      # [x1, y1, x2, y2]
    mask: np.ndarray                # H x W, float32 0~1
    score: float = 0.0              # 분리 신뢰도
    depth_order: int = 0            # 낮을수록 전경
    category: str = "unknown"       # "tree", "lamp", "building"... Phase 2에서 추론
    area_ratio: float = 0.0         # 전체 이미지 대비 면적
    is_animatable: bool = True


@dataclass
class PartCandidate:
    """Spine용으로 쪼갠 오브젝트 파츠 하나."""
    id: str                         # "obj_001_part_01"
    parent_id: str                  # "obj_001"
    name: str                       # "object_01_top"
    mask: np.ndarray
    bbox: list
    category: str = "unknown"
    motion_type: str = "sway"       # "sway", "rotate", "float", "static"
    pivot_hint: Optional[list] = None   # [px, py] 추정 pivot 좌표


@dataclass
class SceneFeatures:
    """BGSceneAnalyze의 출력."""
    canvas_size: list               # [w, h]
    edge_density: float
    dominant_colors: list
    region_proposals: list          # Phase 2에서 실제 구현
    depth_map: Optional[np.ndarray] = None   # Phase 2에서 depth 모델 연동
    analysis_notes: list = field(default_factory=list)


@dataclass
class LayerMetadata:
    """최종 export용 메타데이터."""
    scene_name: str
    canvas_width: int
    canvas_height: int
    objects: list                   # List[ObjectCandidate] → dict
    parts: list                     # List[PartCandidate] → dict
    depth_sorted_ids: list
    export_groups: list
    notes: list = field(default_factory=list)
