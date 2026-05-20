#!/usr/bin/env python3
"""
Expand the Paper 3 MD-DMS production matrix.

Example:

  python scripts/expand_matrix.py \
    --config configs/production_matrix_mvp.yaml \
    --out outputs/paper3_run_matrix_new_mace.csv \
    --include-composition Cu36Zr64 Cu50Zr50

This produces the 8 new MACE runs if Cu64Zr36 is reused from Paper 2.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required. Install it with:\n\n"
            "  pip install pyyaml\n"
        ) from exc

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Config is not a YAML mapping: {path}")

    return data


def period_label(period_ps: float) -> str:
    """Convert 20.0 -> P20, 12.5 -> P12p5."""
    if float(period_ps).is_integer():
        return f"P{int(period_ps)}"
    return "P" + str(period_ps).replace(".", "p")


def gamma_label(gamma: float) -> str:
    """Convert 0.01 -> gam001, 0.005 -> gam0005."""
    text = f"{gamma:g}"
    if text.startswith("0."):
        return "gam" + text[2:]
    return "gam" + text.replace(".", "p")


def require(config: dict[str, Any], key: str) -> Any:
    if key not in config:
        raise KeyError(f"Missing required top-level config key: {key}")
    return config[key]


def build_rows(
    config: dict[str, Any],
    include_compositions: set[str] | None,
    exclude_compositions: set[str],
    reused_compositions: set[str],
    new_only: bool,
) -> list[dict[str, Any]]:
    project = require(config, "project")
    paper = require(config, "paper")

    potential = require(config, "potential")
    system = require(config, "system")
    mddms = require(config, "mddms")
    seeds = require(config, "seeds")
    compositions = require(config, "compositions")

    potential_main = potential["main"]
    potential_label = potential.get("label", potential_main)

    natoms = int(system["natoms"])
    temperature_K = int(system["temperature_K"])

    strain_amplitude = float(mddms["strain_amplitude"])
    periods_ps = [float(x) for x in mddms["periods_ps"]]
    cycles = int(mddms["cycles"])
    timestep_ps = float(mddms["timestep_ps"])

    rows: list[dict[str, Any]] = []

    for comp in compositions:
        name = comp["name"]

        if include_compositions is not None and name not in include_compositions:
            continue

        if name in exclude_compositions:
            continue

        status = "reused" if name in reused_compositions else "new"

        if new_only and status == "reused":
            continue

        cu_fraction = float(comp["cu_fraction"])
        zr_fraction = 1.0 - cu_fraction
        role = comp.get("role", "")

        for seed in seeds:
            for period_ps in periods_ps:
                p_label = period_label(period_ps)
                g_label = gamma_label(strain_amplitude)

                run_name = (
                    f"{paper}_{name}_T{temperature_K}_"
                    f"{potential_label}_seed{seed}_{p_label}_{g_label}"
                )

                rows.append(
                    {
                        "project": project,
                        "paper": paper,
                        "run_name": run_name,
                        "status": status,
                        "composition": name,
                        "cu_fraction": f"{cu_fraction:.6f}",
                        "zr_fraction": f"{zr_fraction:.6f}",
                        "role": role,
                        "potential_main": potential_main,
                        "potential_label": potential_label,
                        "natoms": natoms,
                        "temperature_K": temperature_K,
                        "seed": int(seed),
                        "period_ps": f"{period_ps:.6f}",
                        "strain_amplitude": f"{strain_amplitude:.6f}",
                        "cycles": cycles,
                        "timestep_ps": f"{timestep_ps:.6f}",
                    }
                )

    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        raise ValueError("No rows generated. Check composition filters.")

    fieldnames = list(rows[0].keys())

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Expand Paper 3 composition-sweep matrix into concrete MD-DMS runs."
    )

    parser.add_argument(
        "--config",
        default="configs/production_matrix_mvp.yaml",
        help="Path to Paper 3 YAML matrix config.",
    )

    parser.add_argument(
        "--out",
        default="outputs/paper3_run_matrix.csv",
        help="Output CSV path.",
    )

    parser.add_argument(
        "--include-composition",
        nargs="*",
        default=None,
        help="Only include these compositions.",
    )

    parser.add_argument(
        "--exclude-composition",
        nargs="*",
        default=[],
        help="Exclude these compositions.",
    )

    parser.add_argument(
        "--reuse-composition",
        nargs="*",
        default=[],
        help="Mark these compositions as reused from previous work.",
    )

    parser.add_argument(
        "--new-only",
        action="store_true",
        help="Skip rows marked as reused.",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    out_path = Path(args.out)

    config = load_yaml(config_path)

    include_compositions = (
        set(args.include_composition)
        if args.include_composition is not None and len(args.include_composition) > 0
        else None
    )

    rows = build_rows(
        config=config,
        include_compositions=include_compositions,
        exclude_compositions=set(args.exclude_composition),
        reused_compositions=set(args.reuse_composition),
        new_only=args.new_only,
    )

    write_csv(out_path, rows)

    print(f"Wrote {len(rows)} runs to {out_path}")

    by_composition: dict[str, int] = {}
    for row in rows:
        by_composition[row["composition"]] = by_composition.get(row["composition"], 0) + 1

    print("Runs by composition:")
    for composition, count in sorted(by_composition.items()):
        print(f"  {composition}: {count}")


if __name__ == "__main__":
    main()
