# 修正依頼: GitHub Actions問題対応

## 概要
GitHub Actionsの実行状況を確認した結果、以下のリポジトリで問題が発生しています。

## 問題のあるリポジトリ

### 1. sugipamo/graph_postgres_manager
- **ステータス**: developブランチで4回連続失敗
- **ワークフロー**: Test
- **問題点**:
  1. Docker Composeセットアップ失敗 - Exit code 127 (コマンドが見つからない)
  2. Ruffリンターの失敗 - Exit code 1

### 2. sugipamo/ast2graph
- **ステータス**: 複数のワークフローで失敗
- **ブランチ**: develop
- **問題点**:

#### CIワークフロー
- すべてのプラットフォーム（Ubuntu、macOS、Windows）でテスト失敗
- すべてのPythonバージョン（3.10、3.11、3.12）で失敗
- 主な原因: Ruffリンターのエラー

#### Code Qualityワークフロー
- CodeQL設定の問題によるセキュリティスキャン失敗
- 複数のリンティング違反:
  - 関数命名規則（N802）: `visit_*`メソッドは小文字にすべき
  - 例外処理（B904）: 例外の再発生時に`from`句が欠落
  - コード簡略化（SIM105）: `contextlib.suppress`を使用すべき

## 修正推奨事項

### graph_postgres_manager
1. GitHub ActionsランナーでDocker Composeが利用可能か確認
2. 必要に応じてセットアップステップを追加
3. Ruffリンターのエラーを修正

### ast2graph
1. AST訪問メソッドの命名規則を修正（`visit_`プレフィックスのメソッドを小文字に）
2. 例外処理で`from`句を追加
3. CodeQL設定ファイルを確認・修正
4. その他のリンティング違反を修正

## 優先度
高 - 両リポジトリともCIが失敗しているため、新しい変更のマージが困難な状態です。

## 対応期限
可能な限り早急に対応することを推奨します。