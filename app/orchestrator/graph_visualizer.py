from app.telemetry.logger import get_logger

logger = get_logger()


def to_mermaid(graph) -> str:
    """
    Returns a mermaid diagram of the compiled graph's structure.
    """

    return graph.get_graph().draw_mermaid()


def save_png(graph, path: str) -> bool:
    """
    Attempts to render the graph to a PNG file. Requires network
    access (Mermaid.INK) or optional local deps, so failures are
    logged and swallowed rather than raised.
    """

    try:
        png_bytes = graph.get_graph().draw_mermaid_png()

        with open(path, "wb") as f:
            f.write(png_bytes)

        return True

    except Exception as exc:
        logger.warning(f"Could not render graph PNG: {exc}")

        return False
