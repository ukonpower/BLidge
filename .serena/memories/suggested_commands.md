# 推奨コマンド

## Windowsシステムコマンド

このプロジェクトはWindows環境での開発を想定しています。

### ファイル・ディレクトリ操作
```bash
# ディレクトリ一覧表示
dir
dir <directory>

# ディレクトリ移動
cd <directory>

# ファイル内容表示
type <file>

# ファイル検索
dir /s /b <pattern>
```

### Git操作
```bash
# 状態確認
git status

# コミット履歴
git log --oneline

# 差分確認
git diff

# ブランチ一覧
git branch

# ブランチ切り替え
git checkout <branch>

# 変更をステージング
git add <file>

# コミット
git commit -m "message"

# プッシュ
git push
```

## Blenderアドオン開発

### アドオンのインストール/テスト

1. **手動配置**:
   ```bash
   # blidgeディレクトリをBlenderのaddonsフォルダにコピー
   # 例: C:\Users\<user>\AppData\Roaming\Blender Foundation\Blender\4.2\scripts\addons\
   ```

2. **Blender内での有効化**:
   - `Edit > Preferences > Add-ons > BLidge` で有効化
   - `Install Dependencies` をクリックして依存関係インストール

3. **リロード**:
   - Blenderを再起動、またはF3 → "Reload Scripts"

### 依存関係インストール

アドオンプリファレンスから:
```
Edit > Preferences > Add-ons > BLidge > Install Dependencies
```

これにより`websocket-server`が`blidge/lib/`にインストールされます。

## 開発ワークフロー

### コード変更後
1. ファイルを保存
2. Blenderで `F3` → "Reload Scripts" (または再起動)
3. アドオン機能をテストして動作確認

### デバッグ
- Blenderのシステムコンソール: `Window > Toggle System Console`
- `print()`デバッグが主流
- エラーはコンソールに出力される

## エクスポート/同期コマンド

Blender内のBLidgeパネル(3D Viewサイドバー)から:

- **Sync**: WebSocketサーバー起動/停止
- **Export glTF**: glTF/GLBファイルエクスポート
- **Export scene data**: シーンデータJSON出力

## テスト・リント・フォーマット

**このプロジェクトには自動テスト、リンター、フォーマッターの設定がありません。**

- テストフレームワーク: なし
- リンター: なし
- コードフォーマッター: なし

コード品質は手動レビューと実際のBlender環境でのテストで確認します。

## プロジェクト固有のコマンド

### シーンデータ確認
Blenderで`.blend`ファイルを開き、BLidgeパネルから操作します。

### WebSocketサーバーテスト
```bash
# ブラウザのJavaScriptコンソールから接続テスト
const ws = new WebSocket('ws://localhost:3100');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## 注意事項

- このプロジェクトはBlenderアドオンのため、通常のPython開発とは異なります
- `pip install`等のコマンドは使用しません (アドオン内の依存関係管理を使用)
- Blender Python環境は独立しているため、システムPythonとは分離されています
