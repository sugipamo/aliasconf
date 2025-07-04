# GitHub Actions エラー修正依頼

## 概要
GitHub Actionsで2つのワークフローが失敗しています。

## 問題1: Test Suite - Ruffリンティングエラー

### エラー内容
以下のファイルで空白行に余分な空白文字が含まれています：

1. `src/aliasconf/core/manager.py`
   - 271行目
   - 522行目
   - 528行目
   - 537行目
   - 539行目
   - 542行目
   - 572行目
   - 580行目
   - 583行目
   - 592行目
   - 596行目
   - 602行目
   - 605行目

2. `src/aliasconf/loaders/env_loader.py`
   - 45行目
   - 119行目

3. `tests/core/test_config_manager_env.py`
   - 4-7行目: インポートの並び順
   - 6行目: 未使用のpytestインポート
   - 21行目
   - 30行目
   - 36行目
   - 50行目
   - 63行目
   - 76行目
   - 85行目
   - 91行目

### 修正方法
```bash
# ruffで自動修正を実行
ruff check --fix src/ tests/
```

## 問題2: Deploy Documentation - GitHub Pages未設定

### エラー内容
GitHub Pagesが有効になっていないため、ドキュメントのデプロイが失敗しています。

### 修正方法
1. GitHubリポジトリの設定ページへアクセス: https://github.com/sugipamo/aliasconf/settings/pages
2. "Source"セクションで"GitHub Actions"を選択
3. 保存

## 対応優先度
1. **高**: Ruffリンティングエラーの修正（コード品質に直接影響）
2. **中**: GitHub Pagesの有効化（ドキュメント公開に必要）

## 推奨アクション
1. まず`ruff check --fix`コマンドを実行して自動修正可能なエラーを修正
2. 修正をコミット
3. GitHub Pagesを有効化してドキュメントデプロイを可能にする