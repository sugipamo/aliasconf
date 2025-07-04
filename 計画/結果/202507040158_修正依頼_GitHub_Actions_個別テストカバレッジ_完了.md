# GitHub Actions 個別テストジョブのカバレッジチェック修正依頼

## 問題の概要
GitHub Actionsの個別テストジョブ（integration、performance、edge-cases）でカバレッジチェックが失敗しています。

## エラー詳細
- **integration tests**: カバレッジ 46.96% (必要: 80%)
- **performance tests**: カバレッジ 45.72% (必要: 80%)
- **edge-cases tests**: カバレッジ 54.56% (必要: 80%)

## 原因
個別のテストジョブでは、その特定のテストファイルのみを実行するため、全体のコードカバレッジが低くなっています。これは正常な動作です。

## 修正方針
個別テストジョブではカバレッジチェックを無効化し、統合テストジョブ（all-tests）でのみカバレッジチェックを行うように修正する必要があります。

## 修正内容
`.github/workflows/test.yml`で個別テストジョブのpytestコマンドから`--cov`オプションを削除する。

### 現在の設定（問題あり）
```yaml
- name: Run integration tests
  run: pytest tests/test_integration.py -v --tb=short

- name: Run performance tests  
  run: pytest tests/test_performance.py -v --tb=short

- name: Run edge case tests
  run: pytest tests/test_edge_cases.py -v --tb=short
```

### 修正後の設定
```yaml
- name: Run integration tests
  run: pytest tests/test_integration.py -v --tb=short --no-cov

- name: Run performance tests  
  run: pytest tests/test_performance.py -v --tb=short --no-cov

- name: Run edge case tests
  run: pytest tests/test_edge_cases.py -v --tb=short --no-cov
```

## 期待される結果
- 個別テストジョブはカバレッジチェックなしでテストの成功/失敗のみを判定
- 統合テストジョブ（all-tests）で全体のカバレッジをチェック
- CIパイプライン全体が正常に動作

## 優先度
高 - CIパイプラインが常に失敗している状態のため、早急な修正が必要