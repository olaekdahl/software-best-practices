from pathlib import Path
import sys
import importlib.util
import types

# Allow running this example without installing the package
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PKG_INIT = SRC / "widgetizer" / "__init__.py"

spec = importlib.util.spec_from_file_location("widgetizer", PKG_INIT)
assert spec and spec.loader, "Could not load local widgetizer package."
widgetizer = importlib.util.module_from_spec(spec)
sys.modules["widgetizer"] = widgetizer
spec.loader.exec_module(widgetizer)  # type: ignore[attr-defined]

Widget = widgetizer.Widget
render_markdown = widgetizer.render_markdown
summarize = widgetizer.summarize


def main() -> None:
    cart = Widget(
        name="Cart",
        fields={"items": 3, "total": 59.90},
        tags=["checkout", "cart"],
    )
    product = Widget(
        name="Product",
        fields={"sku": "ABC-123", "price": 19.95},
        tags=["catalog"],
    )

    print(render_markdown(cart))
    print(summarize([cart, product]))


if __name__ == "__main__":
    main()
