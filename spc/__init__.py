"""spc: Statistical Process Control toolkit for quality engineering."""

from .capability import capability, dpmo
from .control_charts import individuals_chart, western_electric_rules, xbar_r_chart
from .msa import gauge_rr

__all__ = [
    "xbar_r_chart",
    "individuals_chart",
    "western_electric_rules",
    "capability",
    "dpmo",
    "gauge_rr",
]
__version__ = "0.1.0"
