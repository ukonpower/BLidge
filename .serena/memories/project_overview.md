# BLidge プロジェクト概要

## プロジェクトの目的

BLidgeは、BlenderのシーンとアニメーションデータをJSON形式でエクスポートし、WebSocketを介してブラウザとリアルタイム同期を行うBlenderアドオンです。クリエイティブコーディングワークフロー向けに設計されており、Blenderシーンをウェブベースのレンダリングエンジンと同期させることを目的としています。

## 技術スタック

- **言語**: Python 3 (Blender 4.2.0以上)
- **フレームワーク**: Blender API (bpy)
- **依存ライブラリ**: 
  - `websocket-server` (WebSocket通信用、`blidge/lib/`に自動インストール)
- **レンダリング**: Blender GPU module (OpenGL)
- **データフォーマット**: JSON, glTF/GLB, Base64エンコード
- **通信プロトコル**: WebSocket

## プロジェクトの種類

- これはBlenderアドオンであり、独立したPythonプロジェクトではありません
- Blenderの`addons`フォルダに配置して使用します
- アドオンの登録システムを使用 (`bpy.utils.register_class`等)

## 主な機能

1. **シーンデータの出力**: シーン情報を解析してJSON形式で保存
2. **glTFエクスポート**: BlenderからglTF(GLB)をエクスポート
3. **リアルタイム同期**: WebSocketサーバーでタイムラインやシーン情報をブラウザへ配信
4. **仮想メッシュ描画**: プリミティブ形状(立方体、球体、平面)をOpenGLで描画

## プラットフォーム

- Windows (開発環境は Windows を想定)
- 標準的なBlender環境で動作
