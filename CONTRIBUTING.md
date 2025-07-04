# Contributing to AliasConf

このドキュメントでは、AliasConfプロジェクトへの貢献方法について説明します。

## 行動規範

このプロジェクトに参加する全ての人は、[行動規範](CODE_OF_CONDUCT.md)を遵守することが求められます。

## 貢献の方法

AliasConfへの貢献には以下のような方法があります：

- バグの報告
- 新機能の提案
- コードの改善
- ドキュメントの改善
- テストの追加
- 他の人の問題解決を支援

## 開発環境のセットアップ

### 前提条件

- Python 3.9以上
- Git
- 仮想環境ツール（venv、virtualenv、pyenvなど）

### セットアップ手順

1. リポジトリをフォーク＆クローン

```bash
git clone https://github.com/YOUR_USERNAME/aliasconf.git
cd aliasconf
```

2. 仮想環境を作成・有効化

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. 開発用依存関係をインストール

```bash
pip install -e ".[dev]"
```

4. 開発環境の確認

```bash
./dev.sh check  # 全てのチェックを実行
```

## コーディング規約

### スタイルガイド

- **Pythonコード**: PEP 8に準拠
- **フォーマッター**: Black（設定済み）
- **インポート順序**: isort（設定済み）
- **Linter**: Ruff（設定済み）

### 型ヒント

- 全ての公開関数・メソッドには型ヒントを付ける
- 複雑な型は`typing`モジュールを使用
- mypyによる型チェックをパス

### ドキュメントストリング

Googleスタイルのドキュメントストリングを使用：

```python
def process_config(config_path: str, validate: bool = True) -> ConfigNode:
    """設定ファイルを処理し、ConfigNodeオブジェクトを返します。
    
    Args:
        config_path: 設定ファイルのパス
        validate: バリデーションを実行するかどうか
        
    Returns:
        処理された設定を含むConfigNodeオブジェクト
        
    Raises:
        ConfigError: 設定ファイルが無効な場合
    """
```

## テストガイドライン

### テストの実行

```bash
# 全てのテストを実行
pytest

# 特定のテストファイルを実行
pytest tests/test_manager.py

# カバレッジレポート付きで実行
pytest --cov=src/aliasconf --cov-report=html
```

### テストの書き方

- 新機能には必ずテストを追加
- エッジケースを考慮
- テストは独立して実行可能
- カバレッジ80%以上を維持

### テスト構造

```python
def test_機能名_条件_期待される結果():
    """テストの説明"""
    # Given: 前提条件の設定
    config = ConfigNode()
    
    # When: テスト対象の実行
    result = config.get("key")
    
    # Then: 結果の検証
    assert result == expected_value
```

## プルリクエストのプロセス

### ブランチ戦略

- `master`: 安定版のコード
- `feature/*`: 新機能の開発
- `fix/*`: バグ修正
- `docs/*`: ドキュメント更新

### コミットメッセージ

以下の形式を使用：

```
<type>: <subject>

<body>

<footer>
```

タイプ：
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: コードスタイル
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他の変更

例：
```
feat: 環境変数サポートを追加

- 環境変数から設定値を読み込む機能を実装
- プレフィックス付き環境変数のサポート
- .envファイルの自動読み込み

Closes #123
```

### プルリクエストの作成

1. フィーチャーブランチを作成
```bash
git checkout -b feature/your-feature-name
```

2. 変更をコミット
```bash
git add .
git commit -m "feat: 新機能の説明"
```

3. フォークにプッシュ
```bash
git push origin feature/your-feature-name
```

4. GitHub上でプルリクエストを作成

### レビュープロセス

- 最低1人のレビュアーの承認が必要
- CIの全チェックがパス
- コードカバレッジが低下しない
- ドキュメントが更新されている

## 問題の報告

### バグレポート

以下の情報を含めてください：

- 環境情報（OS、Pythonバージョン）
- 再現手順
- 期待される動作
- 実際の動作
- エラーメッセージ（ある場合）

### 機能リクエスト

以下を説明してください：

- 解決したい問題
- 提案する解決方法
- 代替案（検討した場合）
- 追加のコンテキスト

## リリースプロセス

1. バージョン番号の更新（セマンティックバージョニング）
2. CHANGELOGの更新
3. タグの作成とプッシュ
4. GitHub Actionsによる自動リリース

## 質問とサポート

- **一般的な質問**: GitHub Discussions
- **バグ報告**: GitHub Issues
- **セキュリティ問題**: security@example.com（※実際のメールアドレスに変更）

## ライセンス

貢献されたコードは、プロジェクトと同じMITライセンスの下でライセンスされます。

## 謝辞

AliasConfプロジェクトへの貢献に感謝します！あなたの協力がこのプロジェクトをより良いものにします。