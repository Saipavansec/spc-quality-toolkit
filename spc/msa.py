"""Gauge R&R by the AIAG MSA range method.

Data layout::

    {part: {operator: [trial readings]}}

Constants K1/K2/K3 follow AIAG MSA 4th edition. Verdicts use the standard
%GRR bands: <10% acceptable, 10-30% marginal, >30% unacceptable.
"""

from __future__ import annotations

import math
import statistics

_K1 = {2: 4.56, 3: 3.05, 4: 2.50}            # by number of trials
_K2 = {2: 3.65, 3: 2.70, 4: 2.30}            # by number of operators
_K3 = {2: 3.65, 3: 2.70, 4: 2.30, 5: 2.08, 6: 1.93,
       7: 1.82, 8: 1.74, 9: 1.67, 10: 1.62}  # by number of parts


def gauge_rr(data):
    """Run a crossed Gauge R&R study; return components and %GRR verdict."""
    parts = sorted(data.keys())
    operators = sorted({op for p in parts for op in data[p].keys()})
    n_parts, n_ops = len(parts), len(operators)
    n_trials = len(data[parts[0]][operators[0]])
    if n_trials not in _K1 or n_ops not in _K2 or n_parts not in _K3:
        raise ValueError(
            "range-method tables cover 2-4 trials, 2-4 operators, 2-10 parts")

    ranges, part_means = [], []
    op_means = {op: [] for op in operators}
    for p in parts:
        p_vals = []
        for op in operators:
            readings = data[p][op]
            ranges.append(max(readings) - min(readings))
            m = statistics.fmean(readings)
            op_means[op].append(m)
            p_vals.extend(readings)
        part_means.append(statistics.fmean(p_vals))

    r_bar = statistics.fmean(ranges)
    ev = r_bar * _K1[n_trials]                                   # repeatability
    op_avgs = [statistics.fmean(op_means[op]) for op in operators]
    xbar_diff = max(op_avgs) - min(op_avgs)
    av = math.sqrt(max((xbar_diff * _K2[n_ops]) ** 2
                       - ev ** 2 / (n_parts * n_trials), 0.0))   # reproducibility
    pv = (max(part_means) - min(part_means)) * _K3[n_parts]      # part variation
    grr = math.hypot(ev, av)
    tv = math.hypot(grr, pv)
    pct_grr = 100 * grr / tv
    return {
        "EV": ev, "AV": av, "GRR": grr, "PV": pv, "TV": tv,
        "%EV": 100 * ev / tv, "%AV": 100 * av / tv,
        "%GRR": pct_grr, "%PV": 100 * pv / tv,
        "ndc": math.floor(1.41 * pv / grr),
        "verdict": ("acceptable" if pct_grr < 10
                    else "marginal" if pct_grr <= 30 else "unacceptable"),
    }
