#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py — CLI entry point for the Choptuik-QCD bridge verification suite.

Modes:
  --mode verify_all       Run all 9 sections
  --mode verify_section   Run specific sections (--sections 1,3,5)
  --mode custom           Run with fully custom parameters from JSON config
  --mode interactive      Interactive menu (default)
  --mode figures          Regenerate all 3D/4D figures only
  --non-interactive       Skip interactive prompts

Language:
  --lang en   English UI (default)
  --lang ru   Russian UI

Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add this dir to path
sys.path.insert(0, str(Path(__file__).parent))

from qcd_bridge_engine import QCDBridgeConfig, run_all
from report_engine import ReportEngine

logger = logging.getLogger("qcd_bridge.cli")

# Default config directory (sibling of this file)
CONFIG_DIR = Path(__file__).parent.parent.parent / "qcd_bridge" / "configs"

I18N = {
    "en": {
        "welcome": "=== Choptuik-QCD Bridge Verification Suite ===",
        "author": "Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701)",
        "choose_mode": "Select run mode:",
        "modes": {
            "1": "Verify all 9 sections (full verification)",
            "2": "Verify specific sections",
            "3": "Custom configuration (arbitrary parameters)",
            "4": "Regenerate all 3D/4D figures",
            "5": "Exit",
        },
        "choose_sections": "Enter section numbers (comma-separated, 1-9): ",
        "choose_config": "Path to custom JSON config: ",
        "running": "Running in mode: {mode}",
        "done": "Done! Reports written to: {dir}",
        "formats": "Report formats (comma-separated, default: all): ",
        "output_dir": "Output directory (default: reports): ",
        "kappa_T": "kappa_T value (default 8.45): ",
        "N": "Hilbert space dimension N (default 28): ",
        "n_flavors": "Number of quark flavors (default 6): ",
        "seed": "Random seed (default 42): ",
        "invalid": "Invalid input, try again.",
        "goodbye": "Goodbye.",
    },
    "ru": {
        "welcome": "=== Система верификации моста Чоптуика–КХД ===",
        "author": "Автор: Ишак Хамзатович Исаев (ORCID 0009-0003-7299-0701)",
        "choose_mode": "Выберите режим работы:",
        "modes": {
            "1": "Верифицировать все 9 разделов (полная проверка)",
            "2": "Верифицировать отдельные разделы",
            "3": "Кастомная конфигурация (произвольные параметры)",
            "4": "Перегенерировать все 3D/4D графики",
            "5": "Выход",
        },
        "choose_sections": "Введите номера разделов через запятую (1-9): ",
        "choose_config": "Путь к кастомному JSON-конфигу: ",
        "running": "Запуск в режиме: {mode}",
        "done": "Готово! Отчёты сохранены в: {dir}",
        "formats": "Форматы отчётов через запятую (по умолчанию: все): ",
        "output_dir": "Каталог вывода (по умолчанию: reports): ",
        "kappa_T": "Значение kappa_T (по умолчанию 8.45): ",
        "N": "Размерность гильбертова пространства N (по умолчанию 28): ",
        "n_flavors": "Число кварковых ароматов (по умолчанию 6): ",
        "seed": "Случайное зерно (по умолчанию 42): ",
        "invalid": "Некорректный ввод, повторите.",
        "goodbye": "До свидания.",
    },
}


def get_default_formats() -> List[str]:
    return ["txt", "csv", "md", "pdf", "html", "docx", "json"]


def parse_formats(s: str) -> List[str]:
    if not s.strip():
        return get_default_formats()
    return [f.strip().lower() for f in s.split(",") if f.strip()]


def interactive_menu(lang: str = "en") -> Optional[Dict[str, Any]]:
    """Show interactive menu and return chosen config."""
    tr = I18N[lang]
    print(f"\n{tr['welcome']}")
    print(tr["author"])
    print()
    while True:
        print(tr["choose_mode"])
        for k, v in tr["modes"].items():
            print(f"  [{k}] {v}")
        choice = input("> ").strip()
        if choice == "5":
            print(tr["goodbye"])
            return None
        if choice == "1":
            return {"mode": "verify_all", "sections": list(range(1, 10)),
                    "language": lang}
        if choice == "2":
            s = input(tr["choose_sections"])
            try:
                sections = [int(x.strip()) for x in s.split(",") if x.strip()]
                sections = [s for s in sections if 1 <= s <= 9]
                if not sections:
                    raise ValueError()
            except ValueError:
                print(tr["invalid"])
                continue
            return {"mode": "verify_section", "sections": sections, "language": lang}
        if choice == "3":
            return {"mode": "custom", "language": lang}
        if choice == "4":
            return {"mode": "figures", "language": lang}
        print(tr["invalid"])


def gather_custom_params(lang: str = "en") -> Dict[str, Any]:
    """Gather custom parameters from user."""
    tr = I18N[lang]
    params: Dict[str, Any] = {"mode": "custom", "language": lang}
    try:
        s = input(tr["kappa_T"])
        params["kappa_T_custom"] = float(s) if s.strip() else 8.45
        s = input(tr["N"])
        params["N_custom"] = int(s) if s.strip() else 28
        s = input(tr["n_flavors"])
        params["n_flavors"] = int(s) if s.strip() else 6
        s = input(tr["seed"])
        params["seed"] = int(s) if s.strip() else 42
        s = input(tr["formats"])
        params["report_formats"] = parse_formats(s)
        s = input(tr["output_dir"])
        params["output_dir"] = s.strip() if s.strip() else "reports"
        params["sections"] = list(range(1, 10))
    except (ValueError, EOFError):
        # Use defaults
        params.setdefault("kappa_T_custom", 8.45)
        params.setdefault("N_custom", 28)
        params.setdefault("n_flavors", 6)
        params.setdefault("seed", 42)
        params.setdefault("report_formats", get_default_formats())
        params.setdefault("output_dir", "reports")
        params.setdefault("sections", list(range(1, 10)))
    return params


def run_pipeline(params: Dict[str, Any], non_interactive: bool = False) -> int:
    """Execute the pipeline per params dict."""
    lang = params.get("language", "en")
    tr = I18N[lang]
    mode = params.get("mode", "verify_all")
    print(f"\n{tr['running'].format(mode=mode)}\n")

    # Build config
    config = QCDBridgeConfig(
        mode=mode,
        sections=params.get("sections", list(range(1, 10))),
        language=lang,
        output_dir=params.get("output_dir", "reports"),
        report_formats=params.get("report_formats", get_default_formats()),
        kappa_T_custom=params.get("kappa_T_custom", 8.45),
        N_custom=params.get("N_custom", 28),
        n_flavors=params.get("n_flavors", 6),
        seed=params.get("seed", 42),
    )

    # Execute
    if mode == "figures":
        # Import and run figure generation
        from generate_figures_3d_4d import generate_all
        sections = config.sections if config.sections else list(range(1, 10))
        manifest = generate_all(sections)
        print(f"\n{tr['done'].format(dir=str(Path(manifest['output_dir'])))}")
        return 0

    result = run_all(config)

    # Generate reports
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    engine = ReportEngine(output_dir=str(output_dir), language=lang)
    paths = engine.generate(result, formats=config.report_formats)

    print(f"\n{tr['done'].format(dir=str(output_dir))}")
    print(f"\nReports generated:")
    for fmt, p in paths.items():
        print(f"  {fmt.upper():6s} -> {p}")
    return 0


def load_config_file(path: str) -> Dict[str, Any]:
    """Load custom config from JSON file."""
    with open(path) as f:
        return json.load(f)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Choptuik-QCD Bridge Verification Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701)",
    )
    parser.add_argument("--mode", choices=["verify_all", "verify_section", "custom", "interactive", "figures"],
                        default="interactive", help="Run mode")
    parser.add_argument("--sections", type=str, default=None,
                        help="Comma-separated section numbers (1-9), for verify_section mode")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to custom JSON config (for custom mode)")
    parser.add_argument("--lang", choices=["en", "ru"], default="en",
                        help="UI language")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Skip interactive prompts (use defaults)")
    parser.add_argument("--output-dir", type=str, default="reports",
                        help="Output directory for reports")
    parser.add_argument("--formats", type=str, default=None,
                        help="Comma-separated report formats (txt,csv,md,pdf,html,docx,json)")
    parser.add_argument("--kappa-T", type=float, default=None,
                        help="Custom kappa_T value")
    parser.add_argument("--N", type=int, default=None,
                        help="Custom Hilbert space dimension")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--list-configs", action="store_true",
                        help="List available preset configs and exit")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")

    if args.list_configs:
        print(f"Available preset configs in {CONFIG_DIR}:")
        if CONFIG_DIR.exists():
            for p in CONFIG_DIR.glob("*.json"):
                print(f"  {p.name}")
        else:
            print("  (none — config dir does not exist)")
        return 0

    # Determine params
    if args.mode == "interactive" and not args.non_interactive:
        params = interactive_menu(args.lang)
        if params is None:
            return 0
        if params.get("mode") == "custom":
            custom = gather_custom_params(args.lang)
            params.update(custom)
    elif args.mode == "custom" and args.config:
        params = load_config_file(args.config)
        params.setdefault("language", args.lang)
    elif args.mode == "verify_section" and args.sections:
        try:
            sections = [int(s.strip()) for s in args.sections.split(",") if s.strip()]
            sections = [s for s in sections if 1 <= s <= 9]
        except ValueError:
            print(f"Invalid --sections: {args.sections}")
            return 1
        params = {"mode": "verify_section", "sections": sections, "language": args.lang,
                  "output_dir": args.output_dir}
        if args.formats:
            params["report_formats"] = parse_formats(args.formats)
        if args.kappa_T is not None:
            params["kappa_T_custom"] = args.kappa_T
        if args.N is not None:
            params["N_custom"] = args.N
        params["seed"] = args.seed
    else:
        # Non-interactive defaults
        params = {"mode": args.mode if args.mode != "interactive" else "verify_all",
                  "sections": list(range(1, 10)), "language": args.lang,
                  "output_dir": args.output_dir, "seed": args.seed}
        if args.formats:
            params["report_formats"] = parse_formats(args.formats)
        if args.kappa_T is not None:
            params["kappa_T_custom"] = args.kappa_T
        if args.N is not None:
            params["N_custom"] = args.N
        if args.mode == "custom" and args.config:
            cfg = load_config_file(args.config)
            params.update(cfg)

    return run_pipeline(params, non_interactive=args.non_interactive)


if __name__ == "__main__":
    sys.exit(main())
