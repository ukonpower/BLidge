# コードスタイルと規約

## 命名規則

### クラス名
- **Blenderクラス**: `BLIDGE_<TYPE>_<Name>` パターン
  - Operator: `BLIDGE_OT_<Name>` (例: `BLIDGE_OT_Sync`)
  - Panel: `BLIDGE_PT_<Name>` (例: `BLIDGE_PT_Controls`)
  - UIList: `BLIDGE_UL_<Name>` (例: `BLIDGE_UL_Uniforms`)
  - PropertyGroup: `BLidge<Name>Property` (例: `BLidgeControlsProperty`)
  
- **一般クラス**: PascalCase (例: `SceneParser`, `AnimationParser`)

### 変数・関数名
- **snake_case**を使用 (例: `get_scene_graph`, `export_gltf_path`)
- **プライベートメソッド**: 特に規約なし(Pythonの慣習に従う)

### モジュール名
- **snake_case**を使用 (例: `scene_parser.py`, `ot_export.py`)
- **接頭辞**:
  - `ot_`: Operator
  - `pt_`: Panel
  - `gzm_`: Gizmo

## 言語

- **すべてのUI文字列とコメントは日本語で記述**
- コード内の変数名・関数名は英語
- docstringは基本的に存在しない (日本語コメントで補完)

## Blender固有の規約

### PropertyGroup
- すべて`bpy.types.PropertyGroup`を継承
- `bpy.props.*Property`でプロパティ定義
- 例:
```python
class BLidgeControlsProperty(bpy.types.PropertyGroup):
    sync_host: bpy.props.StringProperty(name="host", default="localhost")
    sync_port: bpy.props.IntProperty(name="port", default=3100)
```

### Operator
- `bl_idname`: `blidge.<operation_name>`形式 (例: `blidge.sync`)
- `bl_label`: 操作名 (日本語可)
- `execute(self, context)`メソッド必須
- 戻り値: `{'FINISHED'}`, `{'CANCELLED'}`等

### Panel
- `bl_idname`, `bl_label`, `bl_space_type`, `bl_region_type`等を定義
- `draw(self, context)`メソッドでUI描画

### 登録システム
- `classes`リストに全クラスを追加
- `register()`/`unregister()`でループ登録
- カスタムプロパティは`bpy.types.Scene.blidge`、`bpy.types.Object.blidge`に追加

## モジュールリロード

開発時のリロードパターン:
```python
if "bpy" in locals():
    import imp
    imp.reload(ModuleName)
else:
    import bpy
    from .module import ModuleName
```

## 座標系変換

- **Blender座標系**: Y-up
- **カスタム座標系**: Z-up
- **変換式**: `(x, z, -y)` (位置ベクトル、法線等)
- **Y軸プロパティ**: F-Curve IDに反転フラグ付与 (`location_y`, `rotation_euler_y`)

## データエンコーディング

- **メッシュデータ**: Base64エンコード (`utils/base64.py`)
- **ファイルエンコーディング**: UTF-8
- **JSONフォーマット**: インデント付き、読みやすい形式

## 型ヒント

- **ほとんど使用されていない**
- Blender APIの型 (`bpy.types.*`) はアノテーションで使用される場合あり
- 例: `keyframe: bpy.types.Keyframe`

## その他の規約

- **インデント**: タブ使用 (一部スペース混在)
- **文字列**: シングルクォート、ダブルクォート混在
- **インポート順序**: 標準ライブラリ → bpy → 相対インポート
- **エラーハンドリング**: 基本的にシンプル、try-exceptは最小限
