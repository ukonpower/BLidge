# BLidge

BLidge は Blender 向けのアドオンです。シーンやアニメーションを独自の JSON 形式で出力し、
WebSocket を利用してブラウザとリアルタイム連携を行うことを目的としています。

現在は開発途中のため仕様が頻繁に変わります。使用される場合は自己責任でお願いします。

## 主な機能

- **シーンデータの出力** : `blidge.utils.scene_parser.SceneParser` がシーン情報を解析し JSON として保存します。
- **glTF 形式のエクスポート** : `BLIDGE_OT_GLTFExport` オペレーターにより Blender から glTF(GLB) をエクスポートできます。
- **リアルタイム同期** : `BLIDGE_OT_Sync` オペレーターが WebSocket サーバーを起動し、タイムラインやシーン情報をブラウザへ配信します。
- **仮想メッシュ描画** : `blidge.renderer.renderer_virtual_mesh.BLidgeVirtualMeshRenderer` により、プリミティブ形状を OpenGL で描画します。

## ディレクトリ構成

```
blidge/
├── gizmo/                # Gizmo 定義
├── globals/              # プロパティやアドオン設定
├── operators/            # 各種 Operator
├── panels/               # UI パネル
├── renderer/             # ビューポート描画関連
├── ui/                   # UIList など
└── utils/                # 補助スクリプト
```

各モジュールの主な役割は次の通りです。

- **globals** : アドオンで使用する `PropertyGroup` や設定画面 (`AddonPreferences`) を定義します。
- **operators** : エクスポート処理や WebSocket の開始/停止など UI から呼び出される処理をまとめています。
- **panels** : 3D View や Properties に表示される UI パネルを提供します。
- **renderer** : 仮想メッシュを描画するためのシェーダーやジオメトリデータを持ちます。
- **utils** : シーン解析、glTF 設定取得、WebSocket サーバー等の補助機能です。

## 依存ライブラリ

WebSocket 機能には [`websocket-server`](https://pypi.org/project/websocket-server/) を利用します。
アドオンの環境設定 (`Edit > Preferences > Add-ons > BLidge`) から `Install Dependencies` を実行すると、
Blender の Python へ自動でインストールされます。

## 使い方 (概要)

1. このリポジトリを `Blender/Addons` フォルダーに配置し、Blender のアドオンとして有効化します。
2. `BLidge` パネル (3D View のサイドバー) から `Sync` を実行すると WebSocket サーバーが起動します。
   ブラウザ側から `ws://<host>:<port>` へ接続することでシーンデータを受け取れます。
3. `Export glTF` や `Export scene data` ボタンを使用して、それぞれのファイルを出力できます。

詳細な API やデータフォーマットについてはソースコードを参照してください。
