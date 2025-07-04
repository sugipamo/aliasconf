# PyPI初回リリース実施手順

このドキュメントは、AliasConfのPyPI初回リリースを実施するための手順です。

## 前提条件の確認（完了）

✅ **以下の項目は確認済みです**:
- パッケージ名「aliasconf」がPyPIで利用可能
- pyproject.tomlのバージョンが0.1.1に更新済み
- release.ymlワークフローが適切に設定済み
- README.mdが充実した内容で準備完了

## 実施手順

### 1. PyPIアカウントの作成とAPIトークンの取得

1. **PyPIアカウントを作成する**
   - https://pypi.org/account/register/ にアクセス
   - アカウント情報を入力して登録
   - メールアドレスの確認を完了
   - 2要素認証（2FA）を設定することを強く推奨

2. **APIトークンを取得する**
   - PyPIにログイン
   - Account settings → API tokens にアクセス
   - "Add API token" をクリック
   - Token name: `aliasconf-github-actions`
   - Scope: `Entire account`（初回リリースのため）
   - トークンが表示されたらコピー（一度しか表示されません！）

### 2. GitHub Secretsへのトークン登録

1. **GitHubリポジトリの設定を開く**
   - https://github.com/sugipamo/aliasconf/settings/secrets/actions にアクセス
   - "New repository secret" をクリック

2. **シークレットを追加する**
   - Name: `PYPI_API_TOKEN`
   - Value: PyPIで取得したトークン（pypi-で始まる文字列）
   - "Add secret" をクリック

### 3. リリースタグの作成とプッシュ

ターミナルで以下のコマンドを実行：

```bash
# 最新の変更を取得
git pull origin master

# v0.1.1タグを作成
git tag -a v0.1.1 -m "Initial release of AliasConf

- Powerful alias system for configuration management
- Type-safe configuration access
- High performance with caching
- Zero runtime dependencies"

# タグをプッシュ
git push origin v0.1.1
```

### 4. GitHub Releasesからのリリース作成（オプション）

GitHub Actionsがリリースを自動作成しますが、手動で編集したい場合：

1. https://github.com/sugipamo/aliasconf/releases にアクセス
2. 自動作成されたリリースを編集
3. リリースノートを確認・編集

### 5. リリースの確認

1. **GitHub Actionsでワークフローを確認**
   - https://github.com/sugipamo/aliasconf/actions でrelease.ymlワークフローを確認
   - ビルドとPyPIへのアップロードが成功することを確認

2. **PyPIでパッケージを確認**
   - https://pypi.org/project/aliasconf/ にアクセス
   - パッケージが公開されていることを確認

3. **インストールテスト**
   ```bash
   # 新しい仮想環境でテスト
   python -m venv test_install
   source test_install/bin/activate  # Windows: test_install\Scripts\activate
   
   # インストール
   pip install aliasconf
   
   # 動作確認
   python -c "import aliasconf; print(aliasconf.__version__)"
   ```

## トラブルシューティング

### リリースが失敗した場合

1. GitHub Actionsのログを確認
2. 最も一般的な問題：
   - PYPI_API_TOKENが正しく設定されていない
   - パッケージ名が既に使用されている
   - ビルドエラー

### ローカルでのテストビルド

問題がある場合は、ローカルでビルドをテスト：

```bash
# ビルドツールをインストール
pip install build twine

# ビルド
python -m build

# ビルド結果を確認
twine check dist/*
```

## 次のステップ

リリースが成功したら：

1. ドキュメントサイトの公開（計画/202507032315_計画_ドキュメントサイトGitHubPages公開_統合版.md）
2. 環境変数サポートの実装（計画/202507040158_計画_環境変数サポート実装.md）
3. ユーザーフィードバックの収集開始

---

**注意**: このドキュメントは初回リリース専用です。今後のリリースは、タグをプッシュするだけで自動的に実施されます。