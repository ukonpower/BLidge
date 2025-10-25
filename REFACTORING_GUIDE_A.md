# BLidge パーサー設計リファクタリング

## 概要

現在の巨大な `SceneParser` (200行+) を責務ごとに分割。
**設計思想**: Blenderのデータ構造を「パース(解析)」して中間表現(JSON)に変換する。

## 目標

- 各ファイルを100行以下に
- 単一責任原則 (SRP) の遵守
- オブジェクトタイプの追加が容易
- 型ヒントによる安全性向上

---

## ディレクトリ構造

```
blidge/
├── parsers/                        # 新規ディレクトリ
│   ├── __init__.py
│   ├── scene_parser.py             # シーン全体を統括
│   ├── object_parser.py            # オブジェクトパースを統括
│   ├── camera_parser.py            # カメラ専用
│   ├── light_parser.py             # ライト専用
│   ├── mesh_parser.py              # メッシュ専用
│   ├── geometry_parser.py          # プリミティブジオメトリ
│   ├── material_parser.py          # マテリアル処理
│   └── animation_parser.py         # アニメーション処理
│
├── transforms/                      # 新規ディレクトリ
│   ├── __init__.py
│   └── coordinate_converter.py     # 座標変換ユーティリティ
│
└── utils/                           # 既存ディレクトリ
    └── scene_parser.py             # 削除予定
```

---

## 各モジュールの責務

### `transforms/coordinate_converter.py`
- Blender座標系(Y-up) → カスタム座標系(Z-up) の変換
- メソッド: `convert_position()`, `convert_rotation()`, `convert_scale()`, `convert_vector3()`

### `parsers/camera_parser.py`
- カメラオブジェクトのパース
- FOV計算、アスペクト比処理
- メソッド: `parse(obj) -> dict`

### `parsers/light_parser.py`
- ライトオブジェクトのパース
- ライトタイプ(SUN/SPOT等)別のパラメータ処理
- メソッド: `parse(obj) -> dict`

### `parsers/geometry_parser.py`
- プリミティブジオメトリ(cube/sphere/plane)のパース
- 各ジオメトリパラメータの座標変換
- メソッド: `parse(obj) -> dict`

### `parsers/mesh_parser.py`
- メッシュデータのパース
- 頂点、法線、UV、インデックスのBase64エンコード
- メソッド: `parse(obj) -> dict`

### `parsers/material_parser.py`
- マテリアルとユニフォームのパース
- アニメーションアクセサーとの連携
- メソッド: `parse(obj, animation_data) -> dict | None`

### `parsers/animation_parser.py`
- F-Curveのパース
- キーフレームとベジエハンドルの処理
- メソッド: `parse_animation_list() -> dict`

### `parsers/object_parser.py`
- 個別オブジェクトのパース統括
- オブジェクトタイプに応じて専門パーサーに委譲
- 子オブジェクトの再帰的処理
- メソッド: `parse(parent_name) -> dict`

### `parsers/scene_parser.py`
- シーン全体のパース統括
- シーングラフの構築
- アニメーションデータとの統合
- メソッド: `parse_scene() -> dict`

---

## データフロー

```
SceneParser.parse_scene()
  ├─> AnimationParser.parse_animation_list() → アニメーションデータ
  └─> ObjectParser.parse() (ルートオブジェクトごと)
        ├─> CoordinateConverter (位置/回転/スケール)
        ├─> CameraParser.parse() (カメラの場合)
        ├─> LightParser.parse() (ライトの場合)
        ├─> MeshParser.parse() (メッシュの場合)
        ├─> GeometryParser.parse() (プリミティブの場合)
        ├─> MaterialParser.parse()
        └─> ObjectParser.parse() (子オブジェクト、再帰)
```

---

## 実装手順

### Phase 1: 基盤整備
1. `transforms/coordinate_converter.py` 実装
2. `transforms/__init__.py` 作成

### Phase 2: 個別パーサー実装
3. `parsers/camera_parser.py` 実装
4. `parsers/light_parser.py` 実装
5. `parsers/geometry_parser.py` 実装
6. `parsers/mesh_parser.py` 実装
7. `parsers/material_parser.py` 実装
8. `parsers/animation_parser.py` 実装

### Phase 3: 統合
9. `parsers/object_parser.py` 実装
10. `parsers/scene_parser.py` 実装
11. `parsers/__init__.py` 作成

### Phase 4: 移行
12. `operators/ot_export.py` 更新
13. `operators/ot_sync.py` 更新
14. Blenderでテスト
15. `utils/scene_parser.py` 削除

---

## 使用例

```python
# Before (旧設計)
from ..utils.scene_parser import SceneParser
data = SceneParser().get_scene()

# After (新設計)
from ..parsers import SceneParser
data = SceneParser().parse_scene()
```

---

## 設計原則

- **パーサー視点**: データを「エクスポート」ではなく「パース(解析)」
- **単一責任**: 各パーサーは1つのBlenderデータ型のみを理解
- **疎結合**: 専門パーサーは独立してテスト可能
- **型安全**: すべてのメソッドに型ヒント必須
