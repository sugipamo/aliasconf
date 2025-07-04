"""Tests for environment variable loader."""

import os
from unittest import mock

from aliasconf.loaders.env_loader import EnvLoader  # まだ存在しない


def test_env_loader_exists():
    """EnvLoaderクラスが存在することを確認"""
    assert EnvLoader is not None


def test_load_env_var_simple():
    """環境変数から単純な値を読み込めることを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_DATABASE_HOST": "prod.db.com"}):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["database"]["host"] == "prod.db.com"


def test_load_env_var_with_default_prefix():
    """デフォルトプレフィックスで環境変数を読み込めることを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_API_KEY": "secret123"}):
        loader = EnvLoader()
        result = loader.load()
        assert result["api"]["key"] == "secret123"


def test_load_env_var_nested():
    """ネストした構造の環境変数を読み込めることを確認"""
    env_vars = {
        "ALIASCONF_DATABASE__HOST": "localhost",
        "ALIASCONF_DATABASE__PORT": "5432",
        "ALIASCONF_DATABASE__USER": "admin",
    }
    with mock.patch.dict(os.environ, env_vars):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432  # 型変換により整数になる
        assert result["database"]["user"] == "admin"


def test_type_conversion_int():
    """整数への型変換が正しく動作することを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_SERVER_PORT": "8080"}):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["server"]["port"] == 8080
        assert isinstance(result["server"]["port"], int)


def test_type_conversion_bool_true():
    """真偽値（True）への型変換が正しく動作することを確認"""
    true_values = ["true", "True", "TRUE", "1"]
    for value in true_values:
        with mock.patch.dict(os.environ, {"ALIASCONF_DEBUG": value}):
            loader = EnvLoader(prefix="ALIASCONF_")
            result = loader.load()
            assert result["debug"] is True
            assert isinstance(result["debug"], bool)


def test_type_conversion_bool_false():
    """真偽値（False）への型変換が正しく動作することを確認"""
    false_values = ["false", "False", "FALSE", "0"]
    for value in false_values:
        with mock.patch.dict(os.environ, {"ALIASCONF_DEBUG": value}):
            loader = EnvLoader(prefix="ALIASCONF_")
            result = loader.load()
            assert result["debug"] is False
            assert isinstance(result["debug"], bool)


def test_type_conversion_float():
    """浮動小数点数への型変換が正しく動作することを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_RATE": "3.14"}):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["rate"] == 3.14
        assert isinstance(result["rate"], float)


def test_type_conversion_list():
    """リストへの型変換が正しく動作することを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_SERVERS": '["server1", "server2"]'}):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["servers"] == ["server1", "server2"]
        assert isinstance(result["servers"], list)


def test_type_conversion_dict():
    """辞書への型変換が正しく動作することを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_CONFIG": '{"key": "value"}'}):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["config"] == {"key": "value"}
        assert isinstance(result["config"], dict)


def test_custom_delimiter():
    """カスタムデリミタが正しく動作することを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_DATABASE_HOST": "localhost"}):
        loader = EnvLoader(prefix="ALIASCONF_", delimiter="_")
        result = loader.load()
        assert result["database"]["host"] == "localhost"


def test_no_prefix():
    """プレフィックスなしで環境変数を読み込めることを確認"""
    # 環境変数を完全にクリアして、必要なものだけ設定
    with mock.patch.dict(os.environ, {"DATABASE_HOST": "localhost"}, clear=True):
        loader = EnvLoader(prefix="")
        result = loader.load()
        assert result["database"]["host"] == "localhost"


def test_ignore_non_matching_env_vars():
    """プレフィックスに一致しない環境変数は無視されることを確認"""
    env_vars = {"ALIASCONF_INCLUDED": "yes", "OTHER_VAR": "no", "RANDOM": "ignored"}
    with mock.patch.dict(os.environ, env_vars):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert "included" in result
        assert "other" not in result
        assert "random" not in result


def test_empty_env_vars():
    """環境変数が空の場合は空の辞書を返すことを確認"""
    with mock.patch.dict(os.environ, {}, clear=True):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result == {}


def test_type_conversion_disabled():
    """型変換を無効にできることを確認"""
    with mock.patch.dict(os.environ, {"ALIASCONF_PORT": "8080"}):
        loader = EnvLoader(prefix="ALIASCONF_", type_conversion=False)
        result = loader.load()
        assert result["port"] == "8080"
        assert isinstance(result["port"], str)


def test_array_index_support():
    """配列インデックスのサポートを確認"""
    env_vars = {
        "ALIASCONF_SERVERS__0": "server1",
        "ALIASCONF_SERVERS__1": "server2",
        "ALIASCONF_SERVERS__2": "server3",
    }
    with mock.patch.dict(os.environ, env_vars):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["servers"] == ["server1", "server2", "server3"]


def test_complex_nested_structure():
    """複雑なネスト構造の環境変数を読み込めることを確認"""
    env_vars = {
        "ALIASCONF_APP__NAME": "myapp",
        "ALIASCONF_APP__DATABASE__HOST": "localhost",
        "ALIASCONF_APP__DATABASE__PORT": "5432",
        "ALIASCONF_APP__FEATURES__CACHE": "true",
        "ALIASCONF_APP__FEATURES__DEBUG": "false",
    }
    with mock.patch.dict(os.environ, env_vars):
        loader = EnvLoader(prefix="ALIASCONF_")
        result = loader.load()
        assert result["app"]["name"] == "myapp"
        assert result["app"]["database"]["host"] == "localhost"
        assert result["app"]["database"]["port"] == 5432
        assert result["app"]["features"]["cache"] is True
        assert result["app"]["features"]["debug"] is False
