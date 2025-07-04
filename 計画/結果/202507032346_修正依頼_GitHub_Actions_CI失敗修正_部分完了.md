# GitHub Actions CI失敗修正計画 【部分完了】

**ステータス**: 部分完了（2025年7月4日）
- ✅ types-pyyaml追加完了
- ⚠️ isortチェック未実施（環境制約）

## 概要
GitHub ActionsのTest Suiteワークフローがすべてのコミットで失敗している状態です。
主な問題は以下の2点です：

1. **mypy型チェックエラー**: `types-PyYAML`パッケージが不足
2. **isortインポート順序エラー**: インポートの並び順が不適切

## 問題の詳細

### 1. mypy型チェックエラー
```
src/aliasconf/core/manager.py:24: error: Library stubs not installed for "yaml"  [import-untyped]
src/aliasconf/core/manager.py:24: note: Hint: "python3 -m pip install types-PyYAML"
```

- すべてのPythonバージョン（3.8, 3.9, 3.10, 3.11, 3.12）で同じエラーが発生
- すべてのOS（Ubuntu, Windows, macOS）で同じエラーが発生
- `yaml`モジュールの型スタブが不足している

### 2. isortインポート順序エラー
```
ERROR: /home/runner/work/aliasconf/aliasconf/src/aliasconf/core/manager.py Imports are incorrectly sorted and/or formatted.
ERROR: /home/runner/work/aliasconf/aliasconf/src/aliasconf/utils/__init__.py Imports are incorrectly sorted and/or formatted.
ERROR: /home/runner/work/aliasconf/aliasconf/tests/test_edge_cases.py Imports are incorrectly sorted and/or formatted.
ERROR: /home/runner/work/aliasconf/aliasconf/tests/test_basic.py Imports are incorrectly sorted and/or formatted.
```

- Python 3.8環境でのみ検出されている（他のバージョンでは型チェックで先に失敗）
- 4つのファイルでインポート順序が不適切

## 修正方針

### 1. 依存関係の修正
- `pyproject.toml`の`dev-dependencies`に`types-pyyaml`を追加
- 必要に応じて`requirements-dev.txt`にも追加

### 2. インポート順序の修正
- isortを実行して自動修正
- 以下のファイルを修正：
  - `src/aliasconf/core/manager.py`
  - `src/aliasconf/utils/__init__.py`
  - `tests/test_edge_cases.py`
  - `tests/test_basic.py`

### 3. ローカルでの検証
- `mypy src/`を実行して型チェックが通ることを確認
- `isort --check-only src/ tests/`を実行してインポート順序が正しいことを確認
- `pytest`を実行してテストが通ることを確認

## 実行手順

1. `pyproject.toml`に`types-pyyaml`を追加
2. `isort src/ tests/`を実行してインポート順序を自動修正
3. ローカルで全てのチェックを実行して動作確認
4. 修正をコミット＆プッシュ
5. GitHub Actionsでビルドが成功することを確認

## 期待される結果
- すべてのPythonバージョンでmypy型チェックが通過
- すべてのファイルでisortチェックが通過
- Test Suiteワークフローが成功