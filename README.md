# SPC Quality Toolkit

A Python toolkit for Statistical Process Control (SPC), process capability
analysis, and Measurement System Analysis (MSA) — the day-to-day statistical
toolbox of a Quality Engineer.

## Features

- **Control charts** — X-bar & R charts and Individuals (XmR) charts with
  Western Electric run rules (rules 1–4) for out-of-control detection.
- **Process capability** — Cp, Cpk (Cpu/Cpl), plus DPMO and approximate sigma
  level from defect data.
- **MSA** — Gauge R&R by the AIAG range method (%GRR, %PV, ndc, accept/marginal
  verdict).

## Quick start

```bash
pip install -r requirements.txt
python examples/demo.py
```

## Library usage

```python
from spc import xbar_r_chart, capability, gauge_rr, western_electric_rules

chart = xbar_r_chart(measurements, subgroup_size=5)
print(chart["xbar_ucl"], chart["xbar_lcl"])

cap = capability(data, usl=10.5, lsl=9.5)
print(cap["Cp"], cap["Cpk"], cap["capable"])
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## References

- AIAG Statistical Process Control (SPC) reference manual
- AIAG Measurement Systems Analysis (MSA) reference manual
