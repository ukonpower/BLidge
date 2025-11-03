# BLidge データフローとエクスポート関係図

## シーンエクスポートと WebSocket 同期フロー

```mermaid
flowchart TB
    %% エントリポイント
    User[ユーザー操作]

    %% オペレーター
    SyncOp[BLIDGE_OT_Sync<br/>WebSocket同期開始/停止]
    ExportSceneOp[BLIDGE_OT_SceneExport<br/>シーンJSONエクスポート]
    ExportGLTFOp[BLIDGE_OT_GLTFExport<br/>glTF/GLBエクスポート]

    %% メインパーサー
    SceneParser[SceneParser<br/>シーン解析]
    AnimParser[AnimationParser<br/>アニメーション解析]

    %% WebSocketサーバー
    WSServer[WSServer<br/>WebSocketサーバー]

    %% Blenderイベント
    FrameChange[frame_change_post<br/>イベント]
    SavePost[save_post<br/>イベント]
    PlaybackPre[animation_playback_pre<br/>イベント]
    PlaybackPost[animation_playback_post<br/>イベント]

    %% データ構造
    SceneData[シーンデータJSON<br/>- タイムライン情報<br/>- オブジェクト階層<br/>- アニメーションデータ]
    TimelineData[タイムラインデータJSON<br/>- 開始/終了フレーム<br/>- 現在フレーム<br/>- FPS<br/>- 再生状態]
    GLTFFile[glTF/GLBファイル]

    %% クライアント
    Browser[ブラウザクライアント]

    %% フロー: 同期開始
    User -->|同期開始| SyncOp
    SyncOp --> WSServer
    WSServer -->|イベントハンドラー登録| FrameChange
    WSServer -->|イベントハンドラー登録| SavePost
    WSServer -->|イベントハンドラー登録| PlaybackPre
    WSServer -->|イベントハンドラー登録| PlaybackPost

    %% フロー: クライアント接続
    Browser -->|WebSocket接続| WSServer
    WSServer -->|初回接続時| SceneParser

    %% フロー: フレーム変更
    FrameChange -->|フレーム変更検出| WSServer
    WSServer -->|sync/timeline| TimelineData
    TimelineData -->|WebSocket送信| Browser

    %% フロー: シーン保存
    SavePost -->|保存検出| WSServer
    WSServer -->|sync/scene| SceneParser

    %% フロー: シーンエクスポート
    User -->|シーンエクスポート| ExportSceneOp
    ExportSceneOp --> SceneParser
    SceneParser --> SceneData
    SceneData -->|ファイル保存| SceneJSONFile[scene.json]
    SceneParser -->|WebSocket経由| Browser

    %% フロー: glTFエクスポート
    User -->|glTFエクスポート| ExportGLTFOp
    ExportGLTFOp -->|プリセット読み込み| GLTFPreset[glTFプリセット]
    GLTFPreset --> GLTFFile
    ExportGLTFOp -->|event通知| WSServer
    WSServer -->|export_gltf| Browser

    %% フロー: アニメーション解析
    SceneParser --> AnimParser
    AnimParser --> SceneData

    style User fill:#e1f5ff
    style Browser fill:#e1f5ff
    style SyncOp fill:#fff4e1
    style ExportSceneOp fill:#fff4e1
    style ExportGLTFOp fill:#fff4e1
    style SceneParser fill:#f0e1ff
    style AnimParser fill:#f0e1ff
    style WSServer fill:#e1ffe1
    style SceneData fill:#ffe1e1
    style TimelineData fill:#ffe1e1
    style GLTFFile fill:#ffe1e1
```

## シーン解析パイプライン詳細

```mermaid
flowchart TB
    %% エントリポイント
    ParseScene[SceneParser.parse_scene]

    %% アニメーション解析
    ParseAnimList[AnimationParser.parse_animation_list]
    ParseFCurve[AnimationParser.parse_fcurve]
    ParseKeyframes[AnimationParser.parse_keyframe_list]
    ParseKeyframe[AnimationParser.parse_keyframe]
    ParseVector[AnimationParser.parse_vector]

    %% シーングラフ構築
    ParseSceneGraph[SceneParser._parse_scene_graph]

    %% データ変換
    CoordConvert[座標変換<br/>Blender Y-up → Z-up<br/>'x, z, -y']
    Base64Encode[Base64エンコード<br/>メッシュデータ]

    %% 出力データ
    AnimData[アニメーションデータ<br/>- アクセサーID<br/>- F-Curve情報<br/>- キーフレーム<br/>- ベジエハンドル]
    SceneGraph[シーングラフ<br/>- オブジェクト階層<br/>- トランスフォーム<br/>- メッシュデータ<br/>- マテリアル]
    FinalJSON[完全なシーンJSON<br/>- timeline<br/>- animations<br/>- scene_graph]

    %% フロー
    ParseScene --> ParseAnimList
    ParseAnimList --> ParseFCurve
    ParseFCurve --> ParseKeyframes
    ParseKeyframes --> ParseKeyframe
    ParseKeyframe --> ParseVector
    ParseVector --> AnimData

    ParseScene --> ParseSceneGraph
    ParseSceneGraph -->|再帰的にオブジェクト処理| CoordConvert
    ParseSceneGraph -->|メッシュデータ| Base64Encode
    CoordConvert --> SceneGraph
    Base64Encode --> SceneGraph

    AnimData --> FinalJSON
    SceneGraph --> FinalJSON

    %% Blenderデータソース
    BlenderScene[Blenderシーン<br/>- bpy.context.scene]
    BlenderActions[Blenderアクション<br/>- bpy.data.actions]
    BlenderObjects[Blenderオブジェクト<br/>- scene.objects]

    BlenderScene --> ParseScene
    BlenderActions --> ParseAnimList
    BlenderObjects --> ParseSceneGraph

    style ParseScene fill:#f0e1ff
    style ParseAnimList fill:#e1f5ff
    style ParseSceneGraph fill:#e1f5ff
    style AnimData fill:#ffe1e1
    style SceneGraph fill:#ffe1e1
    style FinalJSON fill:#ffd4d4
    style BlenderScene fill:#e1ffe1
    style BlenderActions fill:#e1ffe1
    style BlenderObjects fill:#e1ffe1
```

## アニメーションデータ共有システム

```mermaid
flowchart TB
    %% F-Curveソース
    FCurve[F-Curve<br/>Blenderアクション内]

    %% アクセサー生成
    FCurveManager[FCurveManager<br/>get_fcurve_id]
    AccessorID[アクセサーID<br/>一意識別子]

    %% プロパティリスト
    FCurveList[scene.blidge.fcurve_list<br/>BLidgeAnimationProperty]

    %% 利用箇所
    ObjectAnim[オブジェクトアニメーション<br/>- position<br/>- rotation<br/>- scale]
    MaterialUniform[マテリアルユニフォーム<br/>- as_uniform=True]

    %% エクスポートデータ
    AnimAccessor[アニメーションアクセサー<br/>animations配列]

    %% フロー
    FCurve --> FCurveManager
    FCurveManager --> AccessorID
    AccessorID --> FCurveList
    FCurveList --> ObjectAnim
    FCurveList --> MaterialUniform
    ObjectAnim --> AnimAccessor
    MaterialUniform --> AnimAccessor

    %% データ構造詳細
    AnimAccessor --> KeyframeData[キーフレームデータ<br/>- frame<br/>- value<br/>- handle_left<br/>- handle_right<br/>- interpolation]

    style FCurve fill:#e1ffe1
    style FCurveManager fill:#f0e1ff
    style AccessorID fill:#fff4e1
    style FCurveList fill:#e1f5ff
    style ObjectAnim fill:#ffe1e1
    style MaterialUniform fill:#ffe1e1
    style AnimAccessor fill:#ffd4d4
    style KeyframeData fill:#ffe1f5
```

## WebSocket メッセージタイプ

```mermaid
flowchart LR
    %% メッセージタイプ
    WSMsg[WebSocketメッセージ<br/>JSON形式]

    %% タイプ別
    SyncTimeline[sync/timeline<br/>タイムライン情報]
    SyncScene[sync/scene<br/>シーン全体]
    Event[event<br/>汎用イベント]

    %% データ詳細
    TimelinePayload[データ:<br/>- start_frame<br/>- end_frame<br/>- current_frame<br/>- fps<br/>- is_playing]

    ScenePayload[データ:<br/>- timeline<br/>- animations<br/>- scene_graph]

    EventPayload[データ:<br/>- event_type<br/>- payload<br/>'例: export_gltf']

    %% フロー
    WSMsg --> SyncTimeline
    WSMsg --> SyncScene
    WSMsg --> Event

    SyncTimeline --> TimelinePayload
    SyncScene --> ScenePayload
    Event --> EventPayload

    %% トリガー
    FrameTrigger[トリガー:<br/>frame_change_post] --> SyncTimeline
    SaveTrigger[トリガー:<br/>save_post] --> SyncScene
    ConnectTrigger[トリガー:<br/>クライアント接続] --> SyncScene
    ExportTrigger[トリガー:<br/>glTFエクスポート] --> Event

    style WSMsg fill:#e1f5ff
    style SyncTimeline fill:#fff4e1
    style SyncScene fill:#f0e1ff
    style Event fill:#e1ffe1
    style TimelinePayload fill:#ffe1e1
    style ScenePayload fill:#ffe1e1
    style EventPayload fill:#ffe1e1
```

## 座標系変換

```mermaid
flowchart LR
    %% Blender座標系
    BlenderCoord[Blender座標系<br/>Y-up右手系]

    %% 変換処理
    ConvertPos[位置変換<br/>'x, z, -y']
    ConvertRot[回転変換<br/>'x, z, -y']
    ConvertNormal[法線変換<br/>'x, z, -y']

    %% カスタム座標系
    CustomCoord[カスタム座標系<br/>Z-up右手系]

    %% F-Curve特殊処理
    FCurveY[F-Curve Y軸プロパティ<br/>location_y<br/>rotation_euler_y]
    InvertFlag[反転フラグ<br/>値を負に反転]

    %% フロー
    BlenderCoord --> ConvertPos
    BlenderCoord --> ConvertRot
    BlenderCoord --> ConvertNormal
    ConvertPos --> CustomCoord
    ConvertRot --> CustomCoord
    ConvertNormal --> CustomCoord

    FCurveY --> InvertFlag
    InvertFlag --> CustomCoord

    style BlenderCoord fill:#e1ffe1
    style CustomCoord fill:#ffe1e1
    style ConvertPos fill:#e1f5ff
    style ConvertRot fill:#e1f5ff
    style ConvertNormal fill:#e1f5ff
    style FCurveY fill:#fff4e1
    style InvertFlag fill:#f0e1ff
```

## 注釈

### エクスポートフロー

1. **WebSocket 同期**: リアルタイムでブラウザと Blender を同期
2. **シーンエクスポート**: 完全なシーンデータを JSON 化
3. **glTF エクスポート**: 標準フォーマットでメッシュ/アニメーションを出力

### データ変換

- **座標系**: Blender (Y-up) → カスタム (Z-up) に変換
- **メッシュデータ**: Base64 エンコードで効率的に転送
- **アニメーション**: ベジエハンドル情報を含む完全なキーフレームデータ

### アクセサーシステム

- F-Curve に一意のアクセサー ID を割り当て
- オブジェクトアニメーションとマテリアルユニフォームで共有
- データ重複を避け、効率的なエクスポートを実現
