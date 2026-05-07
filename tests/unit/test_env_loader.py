"""Unit-тесты загрузчика `.env` и нормализации значений переменных."""

from __future__ import annotations

import os

import pytest

from optimizer.common.env_loader import load_env_file


@pytest.mark.unit
def test_env_loader_strips_inline_comment_for_unquoted_values(tmp_path) -> None:
    """Проверяет, что unquoted значение обрезается до `#` inline-комментария."""

    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct # cheap default\n", encoding="utf-8")

    os.environ.pop("OPENROUTER_MODEL", None)
    load_env_file(env_file)
    assert os.environ.get("OPENROUTER_MODEL") == "meta-llama/llama-3.1-8b-instruct"


@pytest.mark.unit
def test_env_loader_keeps_hash_inside_quoted_values(tmp_path) -> None:
    """Проверяет, что quoted значение сохраняет символ `#` как часть значения."""

    env_file = tmp_path / ".env"
    env_file.write_text('PROMPT_TAG="a#b#c"\n', encoding="utf-8")

    os.environ.pop("PROMPT_TAG", None)
    load_env_file(env_file)
    assert os.environ.get("PROMPT_TAG") == "a#b#c"

