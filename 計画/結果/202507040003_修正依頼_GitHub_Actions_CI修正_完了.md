# 修正依頼: GitHub Actions CI修正

## 作成日時
2025-07-04 00:03

## 問題の概要
GitHub ActionsのTest Suiteワークフローが全環境で失敗しています。主に以下の2つの問題が発生しています：

1. **isortエラー** (Python 3.8環境)
   - 4つのファイルでインポートが正しくソートされていない
   - 影響ファイル:
     - `/src/aliasconf/core/manager.py`
     - `/src/aliasconf/utils/__init__.py`
     - `/tests/test_edge_cases.py`
     - `/tests/test_basic.py`

2. **mypyエラー** (全環境)
   - yamlライブラリのタイプスタブがインストールされていない
   - エラーメッセージ: `Library stubs not installed for "yaml"`
   - 推奨される修正: `python3 -m pip install types-PyYAML`

## 修正内容

### 1. isortエラーの修正
以下のコマンドを実行して、インポートを自動的に修正する：
```bash
isort src/ tests/
```

### 2. mypyエラーの修正
以下のいずれかの方法で対応：

#### 方法A: pyproject.tomlにtypes-PyYAMLを追加
```toml
[project.optional-dependencies]
dev = [
    "pytest==8.3.0",
    "pytest-cov==5.0.0",
    "pytest-asyncio==0.23.8",
    "black==24.4.2",
    "ruff==0.5.0",
    "mypy==1.11.0",
    "types-PyYAML",  # 追加
    "isort==5.13.2",
    "sphinx==7.3.7",
    "sphinx-rtd-theme==2.0.0",
    "myst-parser==3.0.1",
]
```

#### 方法B: mypy設定でyamlのチェックを無視
```toml
[tool.mypy]
python_version = "3.8"
strict = true
ignore_missing_imports = true
exclude = ["tests/", "docs/", "build/", "dist/"]

[[tool.mypy.overrides]]
module = "yaml"
ignore_missing_imports = true
```

## 優先度
高 - CIパイプラインが完全に停止しているため、即座の修正が必要

## 推奨される実行順序
1. isortを実行してインポートエラーを修正
2. pyproject.tomlにtypes-PyYAMLを追加
3. ローカルでテストを実行して確認
4. 変更をコミットしてプッシュ

## 期待される結果
- GitHub ActionsのTest Suiteが全環境で正常に動作する
- 今後の開発でCIパイプラインが安定して機能する