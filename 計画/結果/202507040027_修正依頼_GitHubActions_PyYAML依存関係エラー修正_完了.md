# GitHub Actions PyYAML依存関係エラー修正計画

## 作成日時
2025年7月4日 00:27

## 問題の概要
GitHub ActionsのCIパイプラインが全環境で失敗している。主な問題は以下の通り：

1. **PyYAML依存関係エラー**
   - すべてのPythonバージョン（3.8-3.12）でpytestが失敗
   - エラー: `ModuleNotFoundError: No module named 'yaml'`
   - tests/conftest.py:13でimport yamlが失敗

2. **isortインポート順序エラー**（Python 3.8環境）
   - src/aliasconf/core/manager.py
   - src/aliasconf/utils/__init__.py
   - tests/test_edge_cases.py
   - tests/test_basic.py

## 影響範囲
- すべてのテスト環境（Ubuntu、Windows、macOS）
- すべてのPythonバージョン（3.8、3.9、3.10、3.11、3.12）
- 継続的インテグレーションの完全停止

## 原因分析
1. **PyYAML依存関係の問題**
   - テスト環境にPyYAMLがインストールされていない
   - requirements-dev.txtまたはpyproject.tomlに依存関係が明記されていない可能性

2. **isortの設定問題**
   - インポート順序の設定が統一されていない
   - 最新のコミットでインポート順序が変更された可能性

## 修正計画

### 1. PyYAML依存関係の追加
```bash
# pyproject.tomlのtest依存関係を確認・更新
# requirements-dev.txtにPyYAMLを追加
```

### 2. isortのインポート順序修正
```bash
# isort --check-only で問題を確認
# isort . で自動修正を適用
```

### 3. 依存関係の整合性確認
```bash
# すべての開発依存関係が正しくインストールされることを確認
# GitHub Actionsワークフローでの依存関係インストール方法を確認
```

### 4. ローカルでのテスト実行
```bash
# 修正後、ローカルですべてのテストが通ることを確認
pytest -v
isort --check-only .
black --check .
mypy .
```

## 実装手順
1. pyproject.tomlとrequirements-dev.txtを確認し、PyYAMLを追加
2. isortで全ファイルのインポート順序を修正
3. ローカルで全テストを実行して確認
4. 修正をコミットしてプッシュ
5. GitHub Actionsの結果を確認

## 期待される結果
- すべてのテスト環境でpytestが正常に実行される
- isortのチェックが通過する
- CIパイプラインが正常に動作する

## 備考
- 最近のコミットでインポート順序が変更されたため、isortエラーが発生
- PyYAMLはテストで使用されているが、依存関係として明示されていなかった可能性が高い