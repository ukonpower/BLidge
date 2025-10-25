# コードベース構造

## ディレクトリ構成

```
BLidge/
├── blidge/                    # メインアドオンディレクトリ
│   ├── __init__.py           # アドオンエントリポイント、登録システム
│   ├── gizmo/                # Gizmo定義
│   ├── globals/              # プロパティやアドオン設定
│   │   ├── properties.py     # PropertyGroup定義
│   │   ├── preference.py     # AddonPreferences定義
│   │   └── events.py         # イベントハンドラー登録
│   ├── operators/            # 各種Operator
│   │   ├── ot_export.py      # glTF/シーンエクスポート
│   │   ├── ot_sync.py        # WebSocket同期
│   │   ├── ot_fcurve.py      # F-Curve管理
│   │   └── ot_object.py      # オブジェクト操作
│   ├── panels/               # UIパネル
│   │   ├── pt_view_controls.py    # 3D Viewコントロール
│   │   ├── pt_prop_object.py      # オブジェクトプロパティ
│   │   └── pt_graph_fcurve.py     # F-Curveアクセサー
│   ├── renderer/             # ビューポート描画関連
│   │   ├── renderer_virtual_mesh.py  # メインレンダラー
│   │   ├── geometries/       # ジオメトリ定義
│   │   │   ├── geometry_cube.py
│   │   │   ├── geometry_sphere.py
│   │   │   └── geometry_plane.py
│   │   └── shaders/          # シェーダー定義
│   │       └── shader_virtual_mesh.py
│   ├── ui/                   # UIList等
│   │   └── ui_list.py
│   ├── utils/                # 補助スクリプト
│   │   ├── scene_parser.py   # シーン解析
│   │   ├── animation_parser.py  # アニメーション解析
│   │   ├── fcurve_manager.py    # F-Curve管理
│   │   ├── gltf.py           # glTF設定取得
│   │   ├── ws_server.py      # WebSocketサーバー
│   │   └── base64.py         # Base64エンコード
│   └── lib/                  # 依存ライブラリ配置
│       └── websocket_server/ # websocket-server (自動インストール)
├── demo/                     # デモファイル
│   └── demo.blend
├── README.md                 # プロジェクト説明 (日本語)
├── CLAUDE.md                 # Claude Code用ガイダンス (日本語)
└── LICENSE

```

## 主要モジュールの役割

### blidge/__init__.py
- アドオンのエントリポイント
- すべてのクラス(Operator, Panel, PropertyGroup等)の登録
- モジュールリロードシステム (`"bpy" in locals()`パターン)
- `BLidgeVirtualMeshRenderer`のグローバルインスタンス管理

### globals/
- **properties.py**: カスタムプロパティ定義 (PropertyGroup)
  - `BLidgeControlsProperty`: シーン設定 (ホスト/ポート、エクスポートパス等)
  - `BLidgeObjectProperty`: オブジェクト設定 (タイプ、ジオメトリパラメーター等)
  - 各ジオメトリタイプ用のプロパティグループ
- **preference.py**: アドオン設定画面、依存関係インストーラー
- **events.py**: Blenderイベントハンドラー登録/解除

### operators/
- **ot_export.py**: 
  - `BLIDGE_OT_GLTFExport`: glTF/GLBエクスポート
  - `BLIDGE_OT_SceneExport`: シーンデータJSONエクスポート
- **ot_sync.py**: `BLIDGE_OT_Sync` - WebSocketサーバー管理
- **ot_fcurve.py**: F-Curveアクセサー操作
- **ot_object.py**: オブジェクトユニフォーム/アニメーション管理

### panels/
- 3D ViewやPropertiesパネルに表示されるUI
- `BLIDGE_PT_Controls`: メインコントロールパネル
- `BLIDGE_PT_ObjectPropertie`: オブジェクトプロパティパネル
- `BLIDGE_PT_FCurveAccessor`: F-Curveアクセサーパネル

### renderer/
- **renderer_virtual_mesh.py**: `BLidgeVirtualMeshRenderer`
  - `SpaceView3D.draw_handler_add()`でビューポート描画
  - プリミティブ形状の描画 (GPUモジュール使用)
- **geometries/**: 立方体、球体、平面のジオメトリデータ
- **shaders/**: 仮想メッシュ用シェーダー

### utils/
- **scene_parser.py**: `SceneParser` - シーン階層のJSON化
  - `get_scene()`: 完全なシーンデータ取得
  - `get_scene_graph()`: オブジェクト階層構築
  - `get_object_graph()`: 個別オブジェクト変換
- **animation_parser.py**: `AnimationParser` - F-Curveデータ抽出
- **fcurve_manager.py**: F-Curve ID管理
- **gltf.py**: glTFプリセット読み込み
- **ws_server.py**: WebSocketサーバー実装
- **base64.py**: メッシュデータのBase64エンコード

## データフロー

### シーンパース
1. `SceneParser.get_scene()` → シーン全体のエクスポート
2. `SceneParser.get_scene_graph()` → オブジェクト階層を再帰的に構築
3. `SceneParser.get_object_graph()` → 個別オブジェクトをJSONに変換
4. 座標変換: Blender (Y-up) → カスタム (Z-up): `(x, z, -y)`

### アニメーションシステム
- `AnimationParser.get_animation_list()` → F-Curveを抽出
- `scene.blidge.fcurve_list`経由でアクセサーにマッピング
- ベジエハンドル情報を含むキーフレームデータ

### WebSocket同期
- `BLIDGE_OT_Sync`がサーバーライフサイクル管理
- Blenderハンドラー: `frame_change_post`, `save_post`等
- メッセージタイプ: `sync/timeline`, `sync/scene`, `event`
