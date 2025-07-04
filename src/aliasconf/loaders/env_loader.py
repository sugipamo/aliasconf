"""Environment variable loader for AliasConf."""

import os
from typing import Any, Dict, List


class EnvLoader:
    """Environment variable loader."""

    def __init__(
        self,
        prefix: str = "ALIASCONF_",
        delimiter: str = "__",
        type_conversion: bool = True,
    ):
        """Initialize the environment variable loader.

        Args:
            prefix: Prefix for environment variables to load
            delimiter: Delimiter for nested keys
            type_conversion: Whether to convert string values to appropriate types
        """
        self.prefix = prefix
        self.delimiter = delimiter
        self.type_conversion = type_conversion

    def load(self) -> Dict[str, Any]:
        """Load environment variables into a nested dictionary structure.

        Returns:
            Dictionary with loaded configuration
        """
        result: Dict[str, Any] = {}

        for key, value in os.environ.items():
            if self.prefix and not key.startswith(self.prefix):
                continue

            # プレフィックスを削除
            if self.prefix:
                key = key[len(self.prefix) :]

            # キーをパスに分解
            path = self._parse_key(key)
            
            # 空のパスはスキップ
            if not path:
                continue

            # 値を適切な型に変換
            if self.type_conversion:
                value = self._convert_value(value)

            # ネストした辞書構造を作成
            self._set_nested_value(result, path, value)

        return result

    def _parse_key(self, env_key: str) -> List[str]:
        """環境変数キーをパスに分解"""
        # デフォルトデリミタ（__）の場合は特別な処理
        if self.delimiter == "__":
            # まず__で分割
            parts = env_key.split("__")
            # 各パートを_で分割してフラット化
            result = []
            for part in parts:
                if part:
                    result.extend(part.split("_"))
        else:
            # カスタムデリミタの場合はそのまま分割
            parts = env_key.split(self.delimiter)
            result = parts

        # 小文字に変換してフィルタリング
        return [part.lower() for part in result if part]

    def _convert_value(self, value: str) -> Any:
        """値の型変換（文字列→適切な型）"""
        # 空文字列の場合はそのまま返す
        if not value:
            return value

        # ブール値の変換
        if value.lower() in ("true", "1"):
            return True
        elif value.lower() in ("false", "0"):
            return False

        # 数値の変換を試みる
        try:
            # まず整数として解析
            if "." not in value:
                return int(value)
            else:
                # 小数点がある場合は浮動小数点数として解析
                return float(value)
        except ValueError:
            pass

        # JSONとして解析を試みる（リストや辞書の場合）
        if value.startswith(("[", "{")):
            try:
                import json

                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                pass

        # 変換できない場合は文字列として返す
        return value

    def _set_nested_value(
        self, data: Dict[str, Any], path: List[str], value: Any
    ) -> None:
        """ネストした辞書に値を設定"""
        if not path:
            return
            
        current: Any = data

        for i, key in enumerate(path[:-1]):
            # 数値インデックスかどうかチェック
            next_key = path[i + 1] if i + 1 < len(path) else None
            is_next_index = next_key and next_key.isdigit()

            if isinstance(current, dict):
                if key not in current:
                    # 次のキーが数値インデックスの場合はリストを作成
                    if is_next_index:
                        current[key] = []
                    else:
                        current[key] = {}
                elif not isinstance(current[key], (dict, list)):
                    # 既存の値が辞書やリストでない場合は辞書に置き換える
                    current[key] = {}

                current = current[key]

        # 最後のキーが数値インデックスの場合
        final_key = path[-1]
        if final_key.isdigit():
            if isinstance(current, list):
                index = int(final_key)
                # リストを必要なサイズに拡張
                while len(current) <= index:
                    current.append(None)
                current[index] = value
            elif isinstance(current, dict):
                current[final_key] = value
        else:
            if isinstance(current, dict):
                current[final_key] = value
