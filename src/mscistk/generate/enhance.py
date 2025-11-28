"""AI-assisted enhancer that polishes rendered Markdown via a local LLM."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path
from typing import Dict, Iterable, Optional

import yaml

from mscistk.ai.local_llm import LocalLLMClient, LocalLLMConfig, LocalLLMError

DEFAULT_PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def load_settings(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def load_prompt_template(name: str, search_dir: Path) -> str:
    """Load a prompt template by relative name or explicit path."""
    candidate = Path(name)
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")

    prompt_dir = search_dir
    possibilities = [prompt_dir / name]
    if not (prompt_dir / name).suffix:
        possibilities.append((prompt_dir / name).with_suffix(".md"))
        possibilities.append((prompt_dir / name).with_suffix(".txt"))

    for option in possibilities:
        if option.is_file():
            return option.read_text(encoding="utf-8")

    raise FileNotFoundError(f"Prompt template '{name}' not found in {prompt_dir}")


def discover_markdown_files(input_dir: Path) -> Iterable[Path]:
    return sorted(p for p in input_dir.glob("**/*.md") if p.is_file())


def format_prompt(template: str, values: Dict[str, str]) -> str:
    class SafeDict(dict):
        def __missing__(self, key):
            return "{" + key + "}"

    return template.format_map(SafeDict(values))


def enhance_file(
    client: LocalLLMClient,
    prompt_template: str,
    source_path: Path,
    destination: Path,
    *,
    prompt_values: Dict[str, str],
    temperature: float,
    max_tokens: int,
    model: Optional[str],
    dry_run: bool,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        shutil.copy2(source_path, destination)
        return

    source_text = source_path.read_text(encoding="utf-8")
    prompt_values = dict(prompt_values)
    prompt_values.update(
        {
            "document_name": source_path.name,
            "source_markdown": source_text.strip(),
        }
    )

    prompt = format_prompt(prompt_template, prompt_values)

    response = client.generate(
        prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    destination.write_text(response.strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enhance Markdown via local LLM")
    parser.add_argument(
        "--settings",
        type=Path,
        default=Path("src/mscistk/config/settings.example.yaml"),
        help="Path to YAML settings",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("out"),
        help="Directory with rendered Markdown files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("out/ai"),
        help="Directory for AI-enhanced outputs",
    )
    parser.add_argument(
        "--style",
        default="newsletter",
        help="Style key configured under settings.ai.styles",
    )
    parser.add_argument(
        "--prompt",
        help="Optional override for the prompt template file",
    )
    parser.add_argument(
        "--prompt-dir",
        type=Path,
        default=DEFAULT_PROMPT_DIR,
        help="Directory containing prompt templates",
    )
    parser.add_argument(
        "--model",
        help="Override LLM model name",
    )
    parser.add_argument(
        "--language",
        help="Override target output language",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature for the model",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Maximum tokens per completion",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Copy input files to output without contacting an LLM",
    )
    parser.add_argument(
        "--endpoint",
        help="Override local LLM endpoint URL",
    )
    args = parser.parse_args()

    settings = load_settings(args.settings)
    ai_settings = settings.get("ai") or {}
    styles = ai_settings.get("styles") or {}
    style_config = styles.get(args.style, {})

    if not style_config and not args.prompt:
        raise SystemExit(
            f"Style '{args.style}' not configured under settings.ai.styles"
        )

    prompt_name = (
        args.prompt
        or style_config.get("prompt_file")
        or ai_settings.get("default_prompt")
    )
    if not prompt_name:
        raise SystemExit("No prompt template specified for the selected style")

    prompt_template = load_prompt_template(prompt_name, args.prompt_dir)

    endpoint = (
        args.endpoint
        or ai_settings.get("endpoint")
        or LocalLLMConfig().endpoint
    )
    model = args.model or style_config.get("model") or ai_settings.get("default_model")
    language = (
        args.language
        or style_config.get("language")
        or ai_settings.get("language")
        or "de"
    )
    persona = style_config.get("persona", "")
    style_label = style_config.get("style_label", args.style)

    llm_config = LocalLLMConfig(
        endpoint=endpoint,
        default_model=model or LocalLLMConfig().default_model,
        timeout=int(ai_settings.get("timeout", 60)),
        verify_ssl=bool(ai_settings.get("verify_ssl", True)),
    )
    client = LocalLLMClient(llm_config)

    files = list(discover_markdown_files(args.input_dir))
    if not files:
        raise SystemExit(f"No Markdown files found in {args.input_dir}")

    prompt_values = {
        "date": dt.date.today().isoformat(),
        "language": language,
        "persona": persona,
        "style_label": style_label,
    }

    for path in files:
        destination = args.output_dir / path.relative_to(args.input_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            enhance_file(
                client,
                prompt_template,
                path,
                destination,
                prompt_values=prompt_values,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                model=model,
                dry_run=args.skip_llm,
            )
        except LocalLLMError as exc:
            raise SystemExit(f"LLM enhance failed for {path}: {exc}") from exc


if __name__ == "__main__":
    main()
