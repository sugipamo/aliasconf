# GitHub Actions失敗対応計画

## 概要
複数のリポジトリでGitHub Actionsが失敗しています。

## 失敗しているリポジトリと問題

### 1. graph_postgres_manager
- **ワークフロー**: Test
- **問題**: 
  - `docker-compose: command not found` - GitHub ActionsランナーでDocker Composeが利用できない
  - 統合テストが失敗している

### 2. intent_llm
- **ワークフロー**: CI
- **問題**: 依存関係のインストールで失敗している可能性

### 3. ast2graph
- **ワークフロー**: CI, Code Quality
- **問題**:
  - Ruffリンターエラー: `B904` - except句内でのraise文に`from`が必要
  - src/ast2graph/api.py:78行目でエラー

## 修正案

### graph_postgres_manager
1. GitHub Actionsワークフローで`docker compose`（新しいコマンド）を使用するか、`docker-compose`をインストールする
2. または、`services`セクションを使用してPostgreSQLとNeo4jを起動する

### intent_llm
1. 依存関係の問題を詳しく調査
2. pyproject.tomlまたはsetup.pyの設定を確認

### ast2graph
1. src/ast2graph/api.py:78行目を修正:
   ```python
   # 変更前
   raise GraphBuildError(f"Failed to build graph for {file_path}: {str(e)}")
   
   # 変更後
   raise GraphBuildError(f"Failed to build graph for {file_path}: {str(e)}") from e
   ```

## 優先順位
1. ast2graph - 簡単な修正で解決可能
2. graph_postgres_manager - Docker Compose設定の変更が必要
3. intent_llm - 詳細な調査が必要