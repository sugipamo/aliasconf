# GitHub Actions 修正依頼

## 概要
GitHub Actionsのワークフローファイルに複数の問題が発見されました。主に古いバージョンのアクションを使用していることによる非推奨警告と、セキュリティ・パフォーマンスの改善点があります。

## 修正が必要なファイル

### 1. .github/workflows/codeql.yml
**問題点:**
- `actions/checkout@v3` → `@v4`への更新が必要
- `github/codeql-action/*@v2` → `@v3`への更新が必要

**修正内容:**
```yaml
- uses: actions/checkout@v4  # v3からv4へ
- uses: github/codeql-action/init@v3  # v2からv3へ
- uses: github/codeql-action/autobuild@v3  # v2からv3へ
- uses: github/codeql-action/analyze@v3  # v2からv3へ
```

### 2. .github/workflows/release.yml
**問題点:**
- `actions/checkout@v3` → `@v4`への更新が必要
- `actions/setup-python@v4` → `@v5`への更新が必要
- `GITHUB_TOKEN`の明示的な環境変数設定は不要（自動的に提供される）
- PyPIトークンのエラーハンドリングが不足

**修正内容:**
```yaml
- uses: actions/checkout@v4  # v3からv4へ
- uses: actions/setup-python@v5  # v4からv5へ
# GitHub Releaseステップから以下を削除:
# env:
#   GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 3. .github/workflows/test.yml
**問題点:**
- すべてのジョブで`actions/checkout@v3` → `@v4`への更新が必要
- すべてのジョブで`actions/setup-python@v4` → `@v5`への更新が必要
- `codecov/codecov-action@v3` → `@v4`への更新が必要
- ドキュメントビルドジョブが未実装
- パフォーマンス、統合、エッジケーステストが順次実行されている（並列化可能）

**修正内容:**
```yaml
- uses: actions/checkout@v4  # v3からv4へ（全ジョブ）
- uses: actions/setup-python@v5  # v4からv5へ（全ジョブ）
- uses: codecov/codecov-action@v4  # v3からv4へ
```

## 推奨される追加改善

### 1. 依存関係のキャッシュ
pipインストールを高速化するため、以下を追加:
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

### 2. 同時実行制御
同じブランチでの複数実行を防ぐため、各ワークフローに追加:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 3. タイムアウト設定
長時間実行を防ぐため、各ジョブに追加:
```yaml
timeout-minutes: 30
```

### 4. 並列実行の最適化
test.ymlで独立したテストジョブを並列実行するよう修正:
- performance、integration、edge-casesジョブのneeds依存関係を見直し

## 優先度
1. **高**: アクションバージョンの更新（セキュリティとサポートの観点から）
2. **中**: セキュリティ改善（GITHUB_TOKEN削除）
3. **低**: パフォーマンス最適化（キャッシュ、並列化）

## 実施時期
可能な限り早期に実施することを推奨します。特にアクションのバージョン更新は、セキュリティパッチや新機能の恩恵を受けるために重要です。