"""Process capability analysis: Cp, Cpk, DPMO and sigma level."""

from __future__ import annotations

import math
import statistics


def capability(data, usl, lsl):
    """Compute Cp / Cpk from sample data and specification limits.

    Sigma is estimated from the sample standard deviation; for subgrouped
    data prefer a pooled within-subgroup estimate.
    """
    if usl <= lsl:
        raise ValueError("USL must be greater than LSL")
    data = list(data)
    if len(data) < 2:
        raise ValueError("need at least 2 data points")
    mean = statistics.fmean(data)
    sigma = statistics.stdev(data)
    if sigma == 0:
        raise ValueError("zero variation: capability is undefined")
    cp = (usl - lsl) / (6 * sigma)
    cpu = (usl - mean) / (3 * sigma)
    cpl = (mean - lsl) / (3 * sigma)
    cpk = min(cpu, cpl)
    return {
        "n": len(data),
        "mean": mean,
        "sigma": sigma,
        "Cp": cp,
        "Cpk": cpk,
        "Cpu": cpu,
        "Cpl": cpl,
        "capable": cpk >= 1.33,
    }


def dpmo(defects, units, opportunities_per_unit):
    """Defects per million opportunities and approximate sigma level.

    Sigma level uses the standard normal quantile with the conventional
    1.5-sigma shift.
    """
    if units <= 0 or opportunities_per_unit <= 0:
        raise ValueError("units and opportunities must be positive")
    value = defects / (units * opportunities_per_unit) * 1_000_000
    p = min(max(value / 1_000_000, 1e-9), 1 - 1e-9)
    sigma_level = _inv_normal(1 - p) + 1.5
    return {"dpmo": value, "sigma_level": round(sigma_level, 2)}


def _inv_normal(p):
    """Acklam's approximation of the inverse standard normal CDF."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        num = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
        den = ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
        return num / den
    if p <= phigh:
        q = p - 0.5
        r = q * q
        num = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        den = (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
        return num / den
    q = math.sqrt(-2 * math.log(1 - p))
    num = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
    den = ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    return -num / den
