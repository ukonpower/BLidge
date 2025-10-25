# WebSocketプロトコル仕様

## 概要

BLidgeはWebSocketを使用してBlenderとブラウザ間でリアルタイム通信を行います。

## 接続情報

- **デフォルトホスト**: `localhost`
- **デフォルトポート**: `3100`
- **プロトコル**: WebSocket (ws://)
- **設定場所**: `bpy.context.scene.blidge.sync_host`, `sync_port`

## メッセージフォーマット

すべてのメッセージはJSON形式:

```json
{
  "type": "<message_type>",
  "data": <payload>
}
```

## メッセージタイプ

### 1. `sync/timeline`

**送信タイミング**: フレーム変更時 (`frame_change_post`)

**ペイロード**:
```json
{
  "start": <int>,    // タイムライン開始フレーム
  "end": <int>,      // タイムライン終了フレーム
  "current": <int>,  // 現在のフレーム
  "fps": <float>,    // フレームレート
  "playing": <bool>  // 再生中かどうか
}
```

### 2. `sync/scene`

**送信タイミング**: 
- ファイル保存時 (`save_post`)
- 新規クライアント接続時

**ペイロード**: 完全なシーングラフ (JSON)
- オブジェクト階層
- トランスフォーム情報 (座標系変換済み)
- メッシュデータ (Base64エンコード)
- マテリアル情報
- アニメーションデータ (F-Curve、キーフレーム)
- ライト情報
- カメラ情報

構造例:
```json
{
  "scene": {
    "objects": [
      {
        "name": "Cube",
        "type": "MESH",
        "position": [x, z, -y],  // 座標系変換済み
        "rotation": [x, z, -y],
        "scale": [x, y, z],
        "children": [...],
        "animations": [...],
        "material": {...}
      }
    ],
    "animations": {
      "accessors": {...}  // F-Curveアクセサー
    }
  }
}
```

### 3. `event`

**送信タイミング**: 特定のイベント発生時

**ペイロード**:
```json
{
  "type": "<event_type>"
}
```

**イベントタイプ**:
- `export_gltf`: glTFエクスポート完了時

## サーバー実装

### 起動/停止

```python
# 起動
BLIDGE_OT_Sync.execute()  # bl_idname: 'blidge.sync'
→ WSServer.start(host, port)

# 停止
同オペレーター再実行 (トグル動作)
→ WSServer.stop()
```

### ブロードキャスト

```python
BLIDGE_OT_Sync.ws.broadcast(message_type, data)
```

### イベントハンドラー統合

```python
# globals/events.py で登録
bpy.app.handlers.frame_change_post.append(on_frame_change)
bpy.app.handlers.save_post.append(on_save)
bpy.app.handlers.animation_playback_pre.append(on_animation_play)
bpy.app.handlers.animation_playback_post.append(on_animation_stop)
```

## クライアント接続例

### JavaScript (ブラウザ)

```javascript
const ws = new WebSocket('ws://localhost:3100');

ws.onopen = () => {
  console.log('Connected to Blender');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'sync/timeline':
      // タイムライン情報を処理
      console.log('Current frame:', message.data.current);
      break;
      
    case 'sync/scene':
      // シーンデータを処理
      console.log('Scene updated:', message.data);
      break;
      
    case 'event':
      // イベントを処理
      if (message.data.type === 'export_gltf') {
        console.log('glTF exported');
      }
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from Blender');
};
```

## 依存関係

- **ライブラリ**: `websocket-server` (PyPI)
- **インストール先**: `blidge/lib/websocket_server/`
- **インストール方法**: アドオンプリファレンスから "Install Dependencies"

## 実装ファイル

- **サーバー**: `blidge/utils/ws_server.py`
- **オペレーター**: `blidge/operators/ot_sync.py` (`BLIDGE_OT_Sync`)
- **イベント登録**: `blidge/globals/events.py`

## セキュリティとパフォーマンス

- **認証**: なし (ローカルホスト想定)
- **暗号化**: なし (ws://, wss://非対応)
- **メッセージサイズ**: シーンデータは大きくなる可能性あり (Base64エンコードされたメッシュデータ含む)
- **接続数**: 複数クライアント対応 (ブロードキャスト)

## デバッグ

- サーバーログはBlenderシステムコンソールに出力
- ポート使用確認: `netstat -an | findstr 3100` (Windows)
- 接続エラー時はファイアウォール設定を確認
