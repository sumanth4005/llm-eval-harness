"""Evaluate chatbot versions and write a go/no-go report: python run.py"""
import csv
import os

from src.harness import GATE, run


def main():
    summary, rows = run()
    os.makedirs("reports", exist_ok=True)
    with open("reports/scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "version", "f1", "grounded", "unsupported_numbers",
                                          "pii_leak", "pii_types", "refusal_ok"])
        w.writeheader()
        w.writerows(rows)

    lines = ["# Release gate report", "",
             f"Gate: avg F1 >= {GATE['min_avg_f1']}, grounded >= {GATE['min_grounded_rate']:.0%}, "
             f"PII leaks <= {GATE['max_pii_leaks']}, refusals on unsafe asks = {GATE['min_refusal_rate']:.0%}", "",
             "| Version | Avg F1 | Grounded | PII leaks | Refusal rate | Decision |", "|---|---|---|---|---|---|"]
    for v, m in summary.items():
        lines.append(f"| {v} | {m['avg_f1']:.2f} | {m['grounded_rate']:.0%} | {m['pii_leaks']} | "
                     f"{m['refusal_rate']:.0%} | {'GO' if m['passes_gate'] else 'NO-GO'} |")
    lines += ["", "## Failures", ""]
    for r in rows:
        problems = []
        if r["unsupported_numbers"]:
            problems.append(f"unsupported numbers {r['unsupported_numbers']}")
        if r["pii_leak"]:
            problems.append(f"PII leak {r['pii_types']}")
        if not r["refusal_ok"]:
            problems.append("should have refused")
        if problems:
            lines.append(f"- {r['version']} / {r['id']}: " + "; ".join(problems))
    report = "\n".join(lines) + "\n"
    with open("reports/report.md", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
