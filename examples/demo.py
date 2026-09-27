"""Demo: simulate a machining process, chart it, and assess capability + MSA."""

import numpy as np

from spc import (capability, dpmo, gauge_rr, individuals_chart,
                 western_electric_rules, xbar_r_chart)

rng = np.random.default_rng(42)

# --- X-bar & R chart on a stable process (target 10.0 +/- 0.5) ---
stable = rng.normal(10.0, 0.12, size=25 * 5)
chart = xbar_r_chart(stable, subgroup_size=5)
print(f"X-bar: center={chart['xbar_center']:.3f} "
      f"UCL={chart['xbar_ucl']:.3f} LCL={chart['xbar_lcl']:.3f}")
print(f"R:     center={chart['r_center']:.3f} "
      f"UCL={chart['r_ucl']:.3f} LCL={chart['r_lcl']:.3f}")

sigma = (chart["xbar_ucl"] - chart["xbar_center"]) / 3
violations = western_electric_rules(chart["subgroup_means"],
                                    chart["xbar_center"], sigma)
print(f"Western Electric violations on stable process: {len(violations)}")

# --- Same process with a mean shift halfway through ---
shifted = np.concatenate([rng.normal(10.0, 0.12, size=12 * 5),
                          rng.normal(10.35, 0.12, size=13 * 5)])
chart2 = xbar_r_chart(shifted, subgroup_size=5)
sigma2 = (chart2["xbar_ucl"] - chart2["xbar_center"]) / 3
violations2 = western_electric_rules(chart2["subgroup_means"],
                                      chart2["xbar_center"], sigma2)
print(f"Violations after mean shift: {len(violations2)} "
      f"(e.g. {violations2[0][1] if violations2 else 'none'})")

# --- Individuals chart ---
xm = individuals_chart(rng.normal(50, 2, size=30))
print(f"XmR: center={xm['x_center']:.2f} UCL={xm['x_ucl']:.2f} LCL={xm['x_lcl']:.2f}")

# --- Capability ---
cap = capability(rng.normal(10.0, 0.12, size=100), usl=10.5, lsl=9.5)
print(f"Cp={cap['Cp']:.2f} Cpk={cap['Cpk']:.2f} capable={cap['capable']}")

# --- DPMO / sigma level ---
print(dpmo(defects=34, units=10_000, opportunities_per_unit=12))

# --- Gauge R&R: 10 parts x 3 operators x 3 trials ---
parts = range(1, 11)
grr_data = {p: {op: list(rng.normal(10 + p * 0.05 + (op - 1) * 0.01, 0.02, size=3))
                for op in (1, 2, 3)} for p in parts}
grr = gauge_rr(grr_data)
print(f"%GRR={grr['%GRR']:.1f}% ndc={grr['ndc']} verdict={grr['verdict']}")
