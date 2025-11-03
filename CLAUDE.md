# CLAUDE.md

このファイルはClaude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

BLidgeは、BlenderのシーンとアニメーションデータをJSON形式でエクスポートし、WebSocketを介してブラウザとリアルタイム同期を行うBlenderアドオンです。Blenderシーンをウェブベースのレンダリングエンジンと同期させる必要があるクリエイティブコーディングワークフロー向けに設計されています。

## 開発セットアップ

これは独立したPythonプロジェクトではなく、Blenderアドオンです。開発ワークフロー:

1. `blidge`ディレクトリをBlenderのaddonsフォルダに配置
2. Blenderでアドオンを有効化 (編集 > プリファレンス > アドオン > BLidge)
3. アドオンのプリファレンスから依存関係をインストール: `編集 > プリファレンス > アドオン > BLidge > Install Dependencies`

アドオンは`websocket-server`を必要とし、プリファレンスパネルから自動的に`blidge/lib/`にインストールされます。

## アーキテクチャ

### 登録システム

アドオンはBlenderの登録パターンを使用します (`blidge/__init__.py`):
- すべてのオペレーター、パネル、プロパティは`classes`リストに登録されます
- `BLidgeVirtualMeshRenderer`はグローバルにインスタンス化され、個別に管理されます
- カスタムプロパティは`bpy.types.Scene.blidge`と`bpy.types.Object.blidge`に追加されます

### コアデータフロー

**シーンパースパイプライン:**
1. `SceneParser.get_scene()` → シーン全体のエクスポートを統括
2. `SceneParser.get_scene_graph()` → オブジェクト階層を再帰的に構築
3. `SceneParser.get_object_graph()` → 個別のオブジェクトをJSONに変換
4. 座標はBlender (Y-up) からカスタムフォーマット (Z-up) に変換されます: `(x, z, -y)`

**アニメーションシステム:**
- `AnimationParser.get_animation_list()` → すべてのアクションからF-Curveを抽出
- F-Curveは`scene.blidge.fcurve_mappings`を介して「マッパー」にマッピングされます
- アニメーションデータはマッパーIDを介してシーングラフとマテリアルユニフォーム間で共有されます
- キーフレームデータにはベジエ補間用のハンドルが含まれます
- 各アニメーション(`BLidgeAnimationProperty`)には`as_uniform`フラグがあり、マテリアルのUniformとして使用するかどうかを制御できます

**WebSocket同期:**
- `BLIDGE_OT_Sync`オペレーターがWebSocketサーバーのライフサイクルを管理
- Blenderハンドラーを使用: `frame_change_post`, `animation_playback_pre/post`, `save_post`
- フレーム変更時に`sync/timeline`、保存時に`sync/scene`をブロードキャスト
- 新規クライアントは接続時にシーンの完全な状態を受信

### 仮想メッシュレンダリング

`BLidgeVirtualMeshRenderer`はBlenderのGPUモジュールを使用してビューポートにプリミティブ形状(立方体、球体、平面)を描画します:
- `SpaceView3D.draw_handler_add()`経由で実行
- `obj.blidge.render_virtual_mesh == True`のオブジェクトのみをレンダリング
- ジオメトリは`renderer/geometries/`に、シェーダーは`renderer/shaders/`に定義されています
- ワイヤーフレーム/ソリッドシェーディングモードに適応

### プロパティシステム

カスタムプロパティは`globals/properties.py`で定義されています:
- **シーンプロパティ** (`BLidgeControlsProperty`): 同期ホスト/ポート、エクスポートパス、glTFプリセット
- **オブジェクトプロパティ** (`BLidgeObjectProperty`): オブジェクトタイプ、ジオメトリパラメーター、アニメーションリスト
- **アニメーションプロパティ** (`BLidgeAnimationProperty`): アクセサー、編集可能フラグ、`as_uniform`フラグ(Uniformとして使用するかどうか)
- 各ジオメトリタイプ(立方体/球体/平面)には専用のパラメーターグループがあります

## 主要オペレーター

- `blidge.sync` - リアルタイムブラウザ同期用のWebSocketサーバーを起動/停止
- `blidge.export_gltf` - 設定されたプリセットを使用してglTFをエクスポート
- `blidge.export_scene` - シーングラフをJSONにエクスポート
- `blidge.install_dependencies` - websocket-serverを`blidge/lib/`にインストール

## glTFエクスポート

glTFエクスポート (`BLIDGE_OT_GLTFExport`) はBlenderのエクスポートプリセットを読み込みます:
- プリセットファイルがロードされ、実行されてエクスポートパラメーターが設定されます
- 保存時フック: `BLIDGE_OT_GLTFExport.on_save()`は有効化されている場合、自動エクスポートできます
- エクスポート後、WebSocket経由で`export_gltf`タイプの`event`をブロードキャスト

## WebSocketプロトコル

メッセージはJSON形式を使用します: `{"type": "<message_type>", "data": <payload>}`

メッセージタイプ:
- `sync/timeline` - フレーム情報: 開始、終了、現在、fps、再生状態
- `sync/scene` - アニメーション付きの完全なシーングラフ
- `event` - 汎用イベント (例: `export_gltf`)

## モジュールリロード

アドオンは開発用にBlenderの`imp.reload()`パターンを使用します:
- リロードを検出するために`"bpy" in locals()`をチェック
- すべてのインポートされたモジュールがリロードされ、コード変更が反映されます

## コード規約

- 座標変換: Blender Y-up → カスタム Z-up: 位置/法線は`(x, z, -y)`
- メッシュデータは効率的なJSONトランスポートのためにbase64エンコードされます (`utils/base64.py`参照)
- F-Curve IDにはY軸プロパティ用の反転フラグが含まれます (`location_y`, `rotation_euler_y`)
- すべてのUI文字列とコメントは日本語で記述

## Claude Codeとのやり取り

- すべてのやり取りは日本語で行ってください
- このドキュメントも日本語で管理してください
