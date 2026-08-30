from pathlib import Path
import tomllib


def test_didactic_explorer_shell_declares_all_learning_blocks():
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")

    for lesson in ("Signal", "Beam", "Propagation", "Vessel", "Motion"):
        assert f'(\"{lesson}\",' in source


def test_didactic_explorer_shell_uses_stable_signal_renderer_boundary():
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")

    assert "prepare_signal_explorer_comparison" in source
    assert "draw_signal_explorer_comparison" in source
    assert "canvas.figure =" not in source
    assert "Scientific Core" in source


def test_didactic_explorer_has_console_entry_point():
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert config["project"]["scripts"]["hydrosim-didactic"] == (
        "hydrosim.app.didactic_explorer:launch_didactic_explorer"
    )


def test_didactic_explorer_supports_python_module_launch():
    source = Path("src/hydrosim/app/__main__.py").read_text(encoding="utf-8")

    assert "launch_didactic_explorer()" in source
