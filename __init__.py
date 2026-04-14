import sys
import os

# 패키지 루트를 sys.path에 추가
# ComfyUI의 nodes.py와 충돌하지 않도록 상대 import 사용
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from .nodes.bg_scene_analyze import BGSceneAnalyzeNode
from .nodes.bg_object_segment import BGObjectSegmentNode
from .nodes.bg_part_split import BGPartSplitNode
from .nodes.bg_hole_fill import BGHoleFillNode
from .nodes.bg_export_psd import BGExportPSDNode
from .nodes.bg_spine_separator import BackgroundSpineSeparatorNode

NODE_CLASS_MAPPINGS = {
    "BGSceneAnalyze":           BGSceneAnalyzeNode,
    "BGObjectSegment":          BGObjectSegmentNode,
    "BGPartSplit":              BGPartSplitNode,
    "BGHoleFill":               BGHoleFillNode,
    "BGExportPSD":              BGExportPSDNode,
    "BackgroundSpineSeparator": BackgroundSpineSeparatorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BGSceneAnalyze":           "BG: Scene Analyze",
    "BGObjectSegment":          "BG: Object Segment",
    "BGPartSplit":              "BG: Part Split (Spine)",
    "BGHoleFill":               "BG: Hole Fill",
    "BGExportPSD":              "BG: Export PSD/JSON",
    "BackgroundSpineSeparator": "BG: Spine Separator (All-in-One)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
