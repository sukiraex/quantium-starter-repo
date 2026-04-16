from dash.development.base_component import Component
from dash.testing.application_runners import import_app


def iter_components(node):
    """Yield all Dash components recursively from a layout tree."""
    if node is None:
        return
    if isinstance(node, Component):
        yield node
        children = getattr(node, "children", None)
        if children is None:
            return
        if isinstance(children, (list, tuple)):
            for c in children:
                yield from iter_components(c)
        else:
            yield from iter_components(children)
    elif isinstance(node, (list, tuple)):
        for c in node:
            yield from iter_components(c)


def find_by_id(layout, component_id: str):
    for comp in iter_components(layout):
        if getattr(comp, "id", None) == component_id:
            return comp
    return None


app = import_app("app")


def test_header_is_present():
    header = find_by_id(app.layout, "app-header")
    assert header is not None
    # Ensure the header has visible text.
    assert str(header.children).strip() != ""


def test_visualisation_is_present():
    graph = find_by_id(app.layout, "sales-graph")
    assert graph is not None


def test_region_picker_is_present():
    region_picker = find_by_id(app.layout, "region-radio")
    assert region_picker is not None

