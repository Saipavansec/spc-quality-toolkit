"""Unit tests for the spc toolkit (stdlib unittest, no extra deps)."""

import math
import unittest

from spc import (capability, dpmo, gauge_rr, individuals_chart,
                 western_electric_rules, xbar_r_chart)


class TestControlCharts(unittest.TestCase):
    def test_xbar_r_limits_centered(self):
        data = [10.0] * 50  # zero variation edge handled via limits math
        chart = xbar_r_chart([10.0 + (i % 5) * 0.1 for i in range(50)], 5)
        self.assertAlmostEqual(chart["xbar_center"], 10.2, places=6)
        self.assertGreater(chart["xbar_ucl"], chart["xbar_center"])
        self.assertLess(chart["xbar_lcl"], chart["xbar_center"])
        self.assertGreaterEqual(chart["r_lcl"], 0.0)

    def test_xbar_r_bad_subgroup_size(self):
        with self.assertRaises(ValueError):
            xbar_r_chart([1.0] * 20, subgroup_size=11)

    def test_western_electric_rule1(self):
        pts = [0.0] * 10 + [10.0]
        v = western_electric_rules(pts, center=0.0, sigma=1.0)
        self.assertTrue(any("Rule 1" in rule for _, rule in v))

    def test_western_electric_rule4(self):
        pts = [0.5] * 8
        v = western_electric_rules(pts, center=0.0, sigma=1.0)
        self.assertTrue(any("Rule 4" in rule for _, rule in v))

    def test_individuals_chart(self):
        xm = individuals_chart([50.0, 51.0, 49.5, 50.5, 50.2])
        self.assertGreater(xm["x_ucl"], xm["x_center"])
        self.assertGreater(xm["mr_ucl"], 0)


class TestCapability(unittest.TestCase):
    def test_capability_centered(self):
        data = [9.9, 10.0, 10.1, 9.95, 10.05] * 20
        cap = capability(data, usl=10.5, lsl=9.5)
        self.assertGreater(cap["Cp"], 1.0)
        self.assertAlmostEqual(cap["Cp"], cap["Cpk"], places=6)

    def test_dpmo(self):
        r = dpmo(defects=0, units=1000, opportunities_per_unit=1)
        self.assertEqual(r["dpmo"], 0.0)
        r = dpmo(defects=34, units=10_000, opportunities_per_unit=1)
        self.assertAlmostEqual(r["dpmo"], 3400.0)


class TestMSA(unittest.TestCase):
    def test_gauge_rr_good_system(self):
        data = {p: {op: [10.0 + p * 0.5 + (t - 1) * 0.001]
                    for op in (1, 2, 3) for t in (1, 2, 3)}
                for p in range(1, 11)}
        # rebuild nested correctly: {part: {op: [trials]}}
        data = {p: {op: [10.0 + p * 0.5 + t * 0.001 for t in range(3)]
                    for op in (1, 2, 3)} for p in range(1, 11)}
        g = gauge_rr(data)
        self.assertLess(g["%GRR"], 10)
        self.assertEqual(g["verdict"], "acceptable")
        self.assertGreaterEqual(g["ndc"], 5)


if __name__ == "__main__":
    unittest.main()
