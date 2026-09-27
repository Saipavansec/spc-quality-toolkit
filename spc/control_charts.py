"""Control charts for Statistical Process Control (SPC).

Implements X-bar & R charts and Individuals (XmR) charts, plus Western
Electric run rules for detecting out-of-control conditions.
Constants follow the AIAG SPC reference manual.
"""

from __future__ import annotations

import statistics

# Control-chart constants for subgroup sizes 2..10
_A2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483,
       7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}
_D3 = {2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
       7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
_D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004,
       7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}
_D2 = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534,
       7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}


def xbar_r_chart(measurements, subgroup_size=5):
    """Compute X-bar & R chart statistics.

    ``measurements``: flat sequence of readings in time order.
    Returns subgroup statistics, center lines and control limits.
    """
    n = subgroup_size
    if n not in _A2:
        raise ValueError(f"subgroup_size must be 2..10, got {n}")
    k = len(measurements) // n
    if k < 2:
        raise ValueError("need at least 2 full subgroups")
    subgroups = [measurements[i * n:(i + 1) * n] for i in range(k)]
    xbars = [statistics.fmean(g) for g in subgroups]
    ranges = [max(g) - min(g) for g in subgroups]
    xbar_bar = statistics.fmean(xbars)
    r_bar = statistics.fmean(ranges)
    a2, d3, d4 = _A2[n], _D3[n], _D4[n]
    return {
        "subgroup_means": xbars,
        "subgroup_ranges": ranges,
        "xbar_center": xbar_bar,
        "xbar_ucl": xbar_bar + a2 * r_bar,
        "xbar_lcl": xbar_bar - a2 * r_bar,
        "r_center": r_bar,
        "r_ucl": d4 * r_bar,
        "r_lcl": d3 * r_bar,
    }


def individuals_chart(measurements):
    """XmR (individuals & moving range) chart for n=1 data."""
    data = list(measurements)
    if len(data) < 3:
        raise ValueError("need at least 3 measurements")
    mr = [abs(data[i] - data[i - 1]) for i in range(1, len(data))]
    mr_bar = statistics.fmean(mr)
    x_bar = statistics.fmean(data)
    return {
        "individuals": data,
        "moving_ranges": mr,
        "x_center": x_bar,
        "x_ucl": x_bar + 3 * mr_bar / _D2[2],
        "x_lcl": x_bar - 3 * mr_bar / _D2[2],
        "mr_center": mr_bar,
        "mr_ucl": _D4[2] * mr_bar,
    }


def western_electric_rules(points, center, sigma):
    """Apply Western Electric rules 1-4.

    Returns a list of ``(index, rule_description)`` violations.
    """
    pts = list(points)
    violations = []
    # Rule 1: any point beyond 3 sigma
    for i, p in enumerate(pts):
        if abs(p - center) > 3 * sigma:
            violations.append((i, "Rule 1: point beyond 3-sigma limit"))
    # Rule 2: 2 of 3 consecutive beyond 2 sigma, same side
    for i in range(len(pts) - 2):
        w = pts[i:i + 3]
        if sum(1 for p in w if p > center + 2 * sigma) >= 2:
            violations.append((i + 2, "Rule 2: 2 of 3 beyond 2 sigma (above)"))
        if sum(1 for p in w if p < center - 2 * sigma) >= 2:
            violations.append((i + 2, "Rule 2: 2 of 3 beyond 2 sigma (below)"))
    # Rule 3: 4 of 5 consecutive beyond 1 sigma, same side
    for i in range(len(pts) - 4):
        w = pts[i:i + 5]
        if sum(1 for p in w if p > center + sigma) >= 4:
            violations.append((i + 4, "Rule 3: 4 of 5 beyond 1 sigma (above)"))
        if sum(1 for p in w if p < center - sigma) >= 4:
            violations.append((i + 4, "Rule 3: 4 of 5 beyond 1 sigma (below)"))
    # Rule 4: 8 consecutive on the same side of the center line
    for i in range(len(pts) - 7):
        w = pts[i:i + 8]
        if all(p > center for p in w):
            violations.append((i + 7, "Rule 4: 8 consecutive above center"))
        if all(p < center for p in w):
            violations.append((i + 7, "Rule 4: 8 consecutive below center"))
    return violations
