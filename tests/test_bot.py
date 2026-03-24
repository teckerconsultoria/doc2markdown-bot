import ast
import pathlib
import pytest

# Caminho absoluto relativo a este arquivo de teste (tests/test_bot.py → bot.py)
BOT_PATH = pathlib.Path(__file__).parent.parent / "bot.py"


def test_no_get_event_loop_in_bot():
    """bot.py não deve conter asyncio.get_event_loop() (deprecated Python 3.10+)."""
    source = BOT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "get_event_loop":
            pytest.fail(
                f"bot.py linha {node.lineno}: use asyncio.get_running_loop() "
                f"em vez de asyncio.get_event_loop()"
            )
