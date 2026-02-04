"""
KSAU v1.6 verifier (pandas-based).

Note: This file is intentionally named `verify_ksau_1.6.py` for provenance.
It is meant to be executed as a script (not imported as a module).
"""

import pandas as pd
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

CSV_PATH = "KSAU/knotinfo_data_complete.csv"

# KSAU Target Knots (generation labels used by the KSAU mapping)
TARGETS: Dict[str, int] = {"3_1": 1, "6_3": 2, "7_1": 3}

# Comparison knots used in discussions
COMPARISONS: List[str] = ["4_1", "5_1", "5_2"]

ALL_NAMES: List[str] = list(TARGETS.keys()) + COMPARISONS


def _is_empty(x: Any) -> bool:
    if x is None:
        return True
    if isinstance(x, float) and pd.isna(x):
        return True
    s = str(x).strip()
    return s in ("", "0", "nan", "None")


def parse_poly(poly_str: Any) -> Tuple[Dict[int, int], List[int], Optional[int], Optional[int]]:
    """
    Parse a simple Laurent polynomial string into coefficients by exponent.

    Examples accepted (best-effort):
      - -t^(-3)+2*t^(-2)-2*t^(-1)+3-2*t+2*t^2-t^3
      - t^-1+t^-3-t^-4  (integer exponents only)

    Returns:
      (coeff_by_exp, coeff_list_dense, min_exp, max_exp)
    where coeff_list_dense covers [min_exp, ..., max_exp].
    """
    if _is_empty(poly_str):
        return {}, [], None, None

    s = str(poly_str).replace(" ", "")

    # Protect minus signs inside exponent parentheses so splitting doesn't break.
    # Example: t^(-3) -> t^(NEG3)
    s = s.replace("(-", "(NEG")

    terms = re.findall(r"[+-]?[^+-]+", s)

    coeffs: Dict[int, int] = {}
    for term in terms:
        if not term:
            continue
        term = term.replace("NEG", "-")

        m = re.search(r"([a-zA-Z])", term)
        if m:
            var = m.group(1)
            coeff_part, _, exp_part = term.partition(var)

            # Coefficient
            if coeff_part in ("", "+"):
                c = 1
            elif coeff_part == "-":
                c = -1
            else:
                coeff_part_clean = coeff_part.replace("*", "")
                try:
                    c = int(coeff_part_clean)
                except ValueError:
                    c = 1

            # Exponent
            if exp_part == "":
                e = 1
            elif exp_part.startswith("^"):
                exp_val = exp_part[1:].replace("(", "").replace(")", "")
                e = int(exp_val) if exp_val else 1
            else:
                e = 1
        else:
            # Constant term
            try:
                c, e = int(term), 0
            except ValueError:
                continue

        coeffs[e] = coeffs.get(e, 0) + c

    if not coeffs:
        return {}, [], None, None

    min_e = min(coeffs.keys())
    max_e = max(coeffs.keys())
    dense = [coeffs.get(i, 0) for i in range(min_e, max_e + 1)]
    return coeffs, dense, min_e, max_e


def calc_span(min_exp: Optional[int], max_exp: Optional[int]) -> int:
    if min_exp is None or max_exp is None:
        return 0
    return max_exp - min_exp


def is_palindromic_dense(coeffs_dense: List[int]) -> bool:
    return bool(coeffs_dense) and coeffs_dense == coeffs_dense[::-1]


def _try_get(row: pd.Series, keys: Iterable[Any]) -> Any:
    """
    Try multiple column keys (supports both string columns and MultiIndex tuple columns).
    """
    for k in keys:
        try:
            v = row[k]
        except Exception:
            continue
        if not _is_empty(v):
            return v
    return None


def read_knotinfo(csv_path: str) -> pd.DataFrame:
    """
    Best-effort loader for knotinfo_data_complete.csv.

    Supports:
      - pipe-separated with 2-row header (MultiIndex)
      - pipe-separated single header
      - comma-separated single header
    """
    attempts = [
        dict(sep="|", header=[0, 1]),
        dict(sep="|", header=0),
        dict(sep=",", header=0),
    ]

    last_err: Optional[Exception] = None
    for kwargs in attempts:
        try:
            # Treat everything as string to avoid dtype guessing warnings; this is a verifier script.
            df = pd.read_csv(csv_path, dtype=str, low_memory=False, **kwargs)
        except Exception as e:
            last_err = e
            continue

        if "name" in df.columns:
            df = df.set_index("name")
        else:
            df = df.set_index(df.columns[0])

        # sanity check
        if any(k in df.index for k in TARGETS.keys()):
            return df

    raise RuntimeError(f"Failed to read CSV in expected formats: {csv_path}. Last error: {last_err}")


def verify() -> None:
    df = read_knotinfo(CSV_PATH)

    results = []
    for name in ALL_NAMES:
        if name not in df.index:
            continue

        row = df.loc[name]

        alex_str = _try_get(
            row,
            [
                ("alexander_polynomial", "Alexander"),
                ("alexander_polynomial", "alexander_polynomial"),
                "alexander_polynomial",
            ],
        )
        jones_str = _try_get(
            row,
            [
                ("jones_polynomial", "Jones"),
                ("jones_polynomial", "jones_polynomial"),
                "jones_polynomial",
            ],
        )
        sym_type = _try_get(
            row,
            [
                ("symmetry_type", "Symmetry Type"),
                ("symmetry_type", "symmetry_type"),
                "symmetry_type",
            ],
        )

        _, _, alex_min, alex_max = parse_poly(alex_str)
        _, jones_dense, jones_min, jones_max = parse_poly(jones_str)

        alex_span = calc_span(alex_min, alex_max)
        jones_pal = is_palindromic_dense(jones_dense)

        gen = TARGETS.get(name)
        rule_ok = (alex_span == 2 * gen) if gen is not None else None

        results.append(
            {
                "Knot": name,
                "Gen": gen if gen is not None else "-",
                "Alex Span": alex_span,
                "Alex Exp Range": f"[{alex_min},{alex_max}]" if alex_min is not None else "-",
                "Span==2*Gen?": rule_ok if gen is not None else "-",
                "Jones Pal?": jones_pal,
                "Jones Exp Range": f"[{jones_min},{jones_max}]" if jones_min is not None else "-",
                "Symmetry Type": sym_type if sym_type is not None else "Unknown",
                "Jones Coeffs (dense)": jones_dense,
            }
        )

    res_df = pd.DataFrame(results)
    print("\n=== KSAU Validation via Pandas ===\n")
    if res_df.empty:
        print("No target knots found in the CSV.")
        return
    print(res_df.to_string(index=False))


if __name__ == "__main__":
    verify()
