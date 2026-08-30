from pathlib import Path


def test_didactic_explorer_shell_declares_all_learning_blocks():
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")

    for lesson in ("Signal", "Beam", "Propagation", "Vessel", "Motion"):
        assert f'(\"{lesson}\",' in source


def test_didactic_explorer_shell_uses_existing_signal_composition():
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")

    assert "prepare_signal_explorer_comparison" in source
    assert "plot_signal_explorer_comparison" in source
    assert "Scientific Core" in source
