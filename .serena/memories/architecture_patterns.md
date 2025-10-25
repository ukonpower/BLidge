# アーキテクチャパターンとデザイン

## Blenderアドオンの登録パターン

### 基本構造 (`blidge/__init__.py`)

```python
# 1. bl_info定義 (アドオンメタデータ)
bl_info = {
    "name": "blidge",
    "author": "ukonpower",
    "blender": (4, 2, 0),
    "version": (1, 0, 0),
    # ...
}

# 2. モジュールリロードパターン
if "bpy" in locals():
    import imp
    imp.reload(Module1)
    imp.reload(Module2)
else:
    import bpy
    from .module import Module1, Module2

# 3. 登録クラスリスト
classes = [
    Operator1,
    Panel1,
    PropertyGroup1,
    # ...
]

# 4. register/unregister関数
def register():
    # PropertyGroupは個別に登録
    BLidgeProperties.register()
    
    # 他クラスはループで登録
    for c in classes:
        bpy.utils.register_class(c)
    
    # 追加初期化 (レンダラー、イベント等)
    virtualmesh_renderer.start(bpy.context)
    register_event()

def unregister():
    # 逆順でクリーンアップ
    BLidgeProperties.unregister()
    for c in classes:
        bpy.utils.unregister_class(c)
    virtualmesh_renderer.end(bpy.context)
    unregister_event()
```

## データフローパターン

### シーン解析パイプライン

```
SceneParser.get_scene()
    ↓
    ├─ AnimationParser.get_animation_list()  # F-Curve抽出
    │   └─ FCurveManager.get_fcurve_id()     # アクセサーマッピング
    │
    └─ SceneParser.get_scene_graph()         # オブジェクト階層構築
        └─ SceneParser.get_object_graph()    # 個別オブジェクト変換
            ├─ 座標変換 (Y-up → Z-up)
            ├─ メッシュデータBase64エンコード
            └─ マテリアル/アニメーション情報追加
```

### WebSocket通信フロー

```
BLIDGE_OT_Sync.execute()
    ↓
    WSServer.start()  # サーバー起動
    ↓
Blenderイベントハンドラー登録:
    - frame_change_post → broadcast("sync/timeline")
    - save_post → broadcast("sync/scene")
    - animation_playback_pre/post
    ↓
クライアント接続時 → 完全なシーン状態を送信
```

### プロパティアクセスパターン

```python
# シーンプロパティ
bpy.context.scene.blidge.sync_host
bpy.context.scene.blidge.export_gltf_path

# オブジェクトプロパティ
obj.blidge.object_type
obj.blidge.geometry_cube.x
obj.blidge.material.uniform_list
```

## 座標系変換パターン

### Blender → カスタムフォーマット

```python
# Y-up (Blender) → Z-up (カスタム)
def convert_position(blender_vec):
    return (blender_vec.x, blender_vec.z, -blender_vec.y)

# 回転も同様
def convert_rotation(blender_euler):
    return (blender_euler.x, blender_euler.z, -blender_euler.y)
```

### F-Curve反転フラグ

Y軸プロパティ (`location_y`, `rotation_euler_y`) は自動的に値を反転:
```python
fcurve_id = get_fcurve_id(fcurve)
# "location_y" → IDに反転フラグ付与
# AnimationParserでキーフレーム値を反転処理
```

## 仮想メッシュレンダリングパターン

### GPUモジュール使用

```python
class BLidgeVirtualMeshRenderer:
    def start(self, context):
        # ビューポート描画ハンドラー登録
        self._handle = SpaceView3D.draw_handler_add(
            self.draw, 
            (context,), 
            'WINDOW', 
            'POST_VIEW'
        )
    
    def draw(self, context):
        # オブジェクトをフィルタリング
        for obj in context.scene.objects:
            if obj.blidge.render_virtual_mesh:
                # ジオメトリ選択
                # シェーダー適用
                # GPU描画
```

### シェーディングモード対応

```python
# ワイヤーフレーム/ソリッドで描画方法切り替え
shading = context.space_data.shading
if shading.type == 'WIREFRAME':
    gpu.state.depth_test_set('LESS_EQUAL')
else:
    gpu.state.depth_test_set('NONE')
```

## アニメーションデータ共有パターン

### アクセサーシステム

```
F-Curve (Blender Action)
    ↓ get_fcurve_id()
    アクセサーID生成
    ↓
scene.blidge.fcurve_list に登録
    ↓
    ├─ シーングラフのオブジェクトアニメーション
    └─ マテリアルユニフォームアニメーション
    (同じアクセサーIDで参照)
```

## glTFエクスポートパターン

### プリセット読み込み

```python
# Blenderのエクスポートプリセットファイルを動的に読み込み
preset_name = scene.blidge.export_gltf_preset_list
class Container(object):
    __slots__ = ('__dict__',)

op = Container()
file = open(preset_name, 'r')

# プリセット内のPythonコードを実行してパラメーター設定
for line in file.readlines()[3::]:
    exec(line, globals(), locals())

# パラメーターを渡してエクスポート
kwargs = op.__dict__
bpy.ops.export_scene.gltf(**kwargs)
```

## イベント駆動パターン

### Blenderハンドラー登録

```python
def register_event():
    bpy.app.handlers.save_post.append(BLIDGE_OT_GLTFExport.on_save)
    # frame_change_post, animation_playback_pre/post等も同様

def unregister_event():
    bpy.app.handlers.save_post.remove(BLIDGE_OT_GLTFExport.on_save)
```

## 設計上の重要ポイント

1. **Blenderのライフサイクル管理**: register/unregister で適切にリソース解放
2. **リロード対応**: 開発時の快適性のため `imp.reload()` パターン必須
3. **座標系の一貫性**: すべてのエクスポートで同じ変換ルール適用
4. **アクセサーによるデータ共有**: アニメーションデータの重複を避ける
5. **イベント駆動**: リアルタイム同期のため Blender イベントを活用
