# PyPI Release Steps for AliasConf v0.1.1

## 前提条件チェックリスト

✅ GitHubリポジトリ公開済み: https://github.com/sugipamo/aliasconf  
✅ CI/CDパイプライン正常動作中  
✅ 全テスト成功（218件）  
✅ コードカバレッジ85%達成  
✅ pyproject.toml version = "0.1.1"  
✅ release.ymlワークフロー設定済み  
✅ README.mdにインストール手順記載済み  

## 手動実施が必要な手順

### 1. PyPIアカウント作成とトークン取得（ユーザー実施）

1. PyPIアカウント作成: https://pypi.org/account/register/
2. メール認証を完了
3. 2要素認証（2FA）を設定
4. Account settings → API tokens → Add API token
5. Token name: "aliasconf-github-actions"
6. Scope: "Entire account"（初回のため）
7. トークンをコピー（一度しか表示されません！）

### 2. GitHub Secretsへのトークン登録（ユーザー実施）

1. https://github.com/sugipamo/aliasconf/settings/secrets/actions
2. "New repository secret"をクリック
3. Name: `PYPI_API_TOKEN`
4. Value: コピーしたトークン（pypi-で始まる文字列全体）
5. "Add secret"をクリック

### 3. リリースタグの作成とプッシュ

```bash
# タグを作成
git tag -a v0.1.1 -m "Initial PyPI release of AliasConf"

# タグをプッシュ（これによりGitHub Actionsが起動）
git push origin v0.1.1
```

### 4. GitHub Releasesの作成（オプション、推奨）

1. https://github.com/sugipamo/aliasconf/releases/new
2. "Choose a tag" → v0.1.1を選択
3. Release title: "v0.1.1 - Initial PyPI Release"
4. リリースノートをRELEASE_NOTES_v0.1.1.mdからコピー＆ペースト
5. "Publish release"をクリック

### 5. 動作確認

GitHub Actionsが完了後：

```bash
# 新しい仮想環境で確認
python3 -m venv test_env
source test_env/bin/activate
pip install aliasconf==0.1.1

# 動作確認
python -c "import aliasconf; print(aliasconf.__version__)"
```

## トラブルシューティング

### GitHub Actionsが失敗した場合

1. Actions タブで失敗の詳細を確認
2. よくある問題：
   - PYPI_API_TOKEN が正しく設定されていない
   - トークンのスコープが不適切
   - pyproject.tomlの設定に問題

### PyPIにパッケージが表示されない場合

1. https://pypi.org/project/aliasconf/ を確認
2. 数分待ってからリロード（反映に時間がかかることがある）

## 成功後の確認事項

- [ ] https://pypi.org/project/aliasconf/ でパッケージが公開されている
- [ ] pip install aliasconf が成功する
- [ ] インストール後、基本的なサンプルコードが動作する
- [ ] PyPIページに適切な説明が表示されている

## 次のステップ

1. ドキュメントサイトのGitHub Pages公開
2. PyPIバッジをREADME.mdに追加
3. 初期ユーザーへの告知
4. フィードバック収集開始