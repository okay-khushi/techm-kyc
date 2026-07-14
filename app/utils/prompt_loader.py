from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """
    Load a markdown prompt from app/prompts/.
    """

    prompt_path = PROMPTS_DIR / f"{prompt_name}.md"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt '{prompt_name}' not found at {prompt_path}"
        )

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()