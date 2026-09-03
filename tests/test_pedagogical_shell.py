from hydrosim.app.pedagogical_shell import _invoke_builder


def test_invoke_builder_supports_no_argument_builders():
    sentinel = object()

    def builder():
        return sentinel

    assert _invoke_builder(builder, object()) is sentinel


def test_invoke_builder_supplies_figure_canvas_when_declared():
    canvas = object()

    def builder(FigureCanvas):
        return FigureCanvas

    assert _invoke_builder(builder, canvas) is canvas
