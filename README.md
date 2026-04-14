# comfyui-bg-spine-separator

배경 이미지를 **Spine 애니메이션용 오브젝트/파츠 레이어**로 자동 분리하는 ComfyUI 커스텀 노드 패키지.

---

## 주요 기능

- 배경 이미지에서 주요 오브젝트를 개별 레이어(RGBA PNG + 마스크)로 분리
- 오브젝트 제거 후 생긴 빈 영역(hole)을 자동 복원
- Spine 애니메이션에 적합한 파츠 단위로 추가 분해 (crown/trunk, top/base 등)
- PNG, JSON 메타데이터, (Phase 2) PSD 형식으로 출력
- segmentation 백엔드 교체 가능 구조 (Simple → SAM → Grounded SAM)

---

## 설치

### ComfyUI Manager 사용 (권장)

1. ComfyUI Manager → `Install via Git URL`
2. 아래 URL 입력:
   ```
   https://github.com/wmpwookjae/comfyui-bg-spine-separator
   ```
3. ComfyUI 재시작

### 수동 설치

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/wmpwookjae/comfyui-bg-spine-separator
cd comfyui-bg-spine-separator
pip install -r requirements.txt
```

> **주의**: `opencv-contrib-python` 이 필요합니다. `opencv-python`만 설치된 경우 saliency 기능이 동작하지 않을 수 있습니다.

---

## 노드 목록

| 노드 | 역할 |
|---|---|
| **BG: Spine Separator (All-in-One)** | 전체 파이프라인 올인원 실행 |
| **BG: Scene Analyze** | 장면 분석 (edge density, region proposals) |
| **BG: Object Segment** | 오브젝트 마스크 분리 |
| **BG: Part Split (Spine)** | Spine용 파츠 분해 |
| **BG: Hole Fill** | 오브젝트 제거 후 배경 복원 |
| **BG: Export PSD/JSON** | PNG / JSON / PSD 출력 |

---

## 빠른 시작

### 올인원 노드 (권장)

```
LoadImage → BG: Spine Separator (All-in-One)
```

파라미터:
- `preset`: `spine_ready` (기본값)
- `segmentation_backend`: `simple` (Phase 1 기본값)
- `enable_part_split`: True
- `enable_hole_fill`: True

### 단계별 노드

```
LoadImage
  └→ BG: Scene Analyze
       └→ BG: Object Segment
            ├→ BG: Part Split (Spine)
            ├→ BG: Hole Fill
            └→ BG: Export PSD/JSON
```

---

## 출력 폴더 구조

```
ComfyUI/output/
  {scene_name}_{timestamp}/
    layers/
      bg_filled.png               ← hole fill된 배경 plate
      obj_001_object_01.png       ← RGBA (마스크=알파)
      obj_001_part_01_crown.png
    masks/
      obj_001_object_01_mask.png  ← 흑백 마스크
    metadata/
      layers.json                 ← 전체 레이어 구조
    psd/
      (Phase 2에서 추가)
```

---

## 프리셋 설명

| 프리셋 | 설명 | max_objects | min_area_ratio |
|---|---|---|---|
| `conservative` | 큰 오브젝트만. 과분리 방지 최우선. | 5 | 0.05 |
| `spine_ready` | 일반 배경 씬 기본값. | 10 | 0.02 |
| `fx_heavy` | 구름/잎/장식 같이 작은 요소까지. | 15 | 0.01 |
| `architecture` | 건물/창문/간판 중심 씬. | 8 | 0.03 |

---

## 실패 유형 대응

| 증상 | 해결 방법 |
|---|---|
| 오브젝트가 너무 잘게 쪼개짐 (F1 과분리) | `min_area_ratio` 증가 또는 `conservative` 프리셋 사용 |
| 오브젝트가 배경과 붙어서 안 떨어짐 (F2 미분리) | `prompt_hint` 입력 또는 `fx_heavy` 프리셋 사용 |
| hole fill 후 배경 선이 끊김 (F3 구조 붕괴) | `fill_radius` 줄이기 |
| 오브젝트 테두리에 배경색이 남음 (F4 가장자리 오염) | `mask_smoothness` 증가 |

---

## 개발 로드맵

- **Phase 1 (현재)**: Simple segmenter, Fast hole fill, PNG + JSON export
- **Phase 2**: SAM 백엔드, Depth 정렬, PSD export, 네이밍 개선
- **Phase 3**: Grounded SAM (prompt_hint 실제 활용), AI inpaint, Spine JSON 직접 export

---

## 주의사항

- 이 노드는 **배경 전용**입니다. 캐릭터 컷아웃에는 적합하지 않습니다.
- Phase 1의 segmentation 품질은 saliency 기반으로 완벽하지 않습니다. 수작업 후보정의 출발점으로 사용하세요.
- `export_psd=True`는 Phase 2 이후에 활성화 예정입니다. 현재는 False로 두세요.
