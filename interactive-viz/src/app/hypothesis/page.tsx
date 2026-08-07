"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LiveChart } from "@/components/live-chart";
import { MetricCard } from "@/components/metric-card";
import {
  runHypothesisTest,
  deltaBC,
  deltaAC,
  choptyukBase,
  choptyukFull,
  diracTrivial,
  spinorDeltaA,
  spinorDeltaB,
  CHOPTYUK_REFERENCE,
  DIRAC_REFERENCE,
} from "@/lib/compute";
import type { HypothesisTest } from "@/lib/types";
import { FlaskConical, Plus, Trash2 } from "lucide-react";

interface HypothesisInput {
  name: string;
  computed: string;
  reference: string;
  tolerance: string;
}

const DEFAULT_HYPOTHESES: HypothesisInput[] = [
  {
    name: "Δ_{bC}",
    computed: DIRAC_REFERENCE.delta_bC.toString(),
    reference: "3.438710",
    tolerance: "0.01",
  },
  {
    name: "Δ_{aC}",
    computed: "0.000828",
    reference: "0.000828",
    tolerance: "0.001",
  },
  {
    name: "Δ_{Ch,base}",
    computed: CHOPTYUK_REFERENCE.Delta_Ch_base.toString(),
    reference: "3.437883",
    tolerance: "0.01",
  },
  {
    name: "Δ_{Ch,full}",
    computed: CHOPTYUK_REFERENCE.Delta_Ch_full.toString(),
    reference: "3.447040",
    tolerance: "0.01",
  },
  {
    name: "b_Ch",
    computed: CHOPTYUK_REFERENCE.b_Ch.toString(),
    reference: "0.376510",
    tolerance: "0.001",
  },
];

export default function HypothesisPage() {
  const [hypotheses, setHypotheses] = useState<HypothesisInput[]>(DEFAULT_HYPOTHESES);
  const [sweepParam, setSweepParam] = useState("b_Ch");
  const [sweepMin, setSweepMin] = useState("0");
  const [sweepMax, setSweepMax] = useState("1");
  const [sweepSteps, setSweepSteps] = useState("50");

  // Run tests
  const results: HypothesisTest[] = useMemo(
    () =>
      hypotheses.map((h) =>
        runHypothesisTest(
          h.name,
          parseFloat(h.computed),
          parseFloat(h.reference),
          parseFloat(h.tolerance)
        )
      ),
    [hypotheses]
  );

  const passCount = results.filter((r) => r.passed).length;

  // Sweep data
  const sweepData = useMemo(() => {
    const min = parseFloat(sweepMin);
    const max = parseFloat(sweepMax);
    const steps = parseInt(sweepSteps);
    if (isNaN(min) || isNaN(max) || isNaN(steps)) return [];

    const deltaA = spinorDeltaA();
    const deltaB = spinorDeltaB();
    const deltaC = Math.PI / 7;
    const lTriv = diracTrivial(3, -2);
    const dBC = deltaBC(lTriv, deltaA, deltaB, deltaC);
    const dAC = deltaAC(deltaC, -2);
    const chBase = choptyukBase(dBC, dAC, -2, 3);

    const data: Record<string, unknown>[] = [];
    for (let i = 0; i <= steps; i++) {
      const t = min + (max - min) * (i / steps);
      const row: Record<string, unknown> = { x: t.toFixed(4) };

      if (sweepParam === "b_Ch") {
        row["Δ_{Ch}"] = choptyukFull(chBase, t, deltaA);
      } else if (sweepParam === "δ_C") {
        const lT = diracTrivial(3, -2);
        const bc = deltaBC(lT, deltaA, deltaB, t);
        const ac = deltaAC(t, -2);
        const cb = choptyukBase(bc, ac, -2, 3);
        row["Δ_{Ch}"] = choptyukFull(cb, 0.376510, deltaA);
      } else {
        row["Δ_{Ch}"] = chBase + t;
      }
      row["Reference"] = 3.443;
      data.push(row);
    }
    return data;
  }, [sweepParam, sweepMin, sweepMax, sweepSteps]);

  const addHypothesis = () => {
    setHypotheses((prev) => [
      ...prev,
      { name: "New Test", computed: "0", reference: "0", tolerance: "0.01" },
    ]);
  };

  const removeHypothesis = (idx: number) => {
    setHypotheses((prev) => prev.filter((_, i) => i !== idx));
  };

  const updateHypothesis = (idx: number, field: keyof HypothesisInput, value: string) => {
    setHypotheses((prev) =>
      prev.map((h, i) => (i === idx ? { ...h, [field]: value } : h))
    );
  };

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Hypothesis Testing</h1>
          <p className="text-sm text-gray-400 mt-1">
            Custom parameter tests with real-time comparison
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <Badge variant={passCount === results.length ? "success" : "destructive"}>
            {passCount}/{results.length} passed
          </Badge>
          <Button variant="outline" size="sm" onClick={addHypothesis}>
            <Plus className="h-4 w-4 mr-1" />
            Add Test
          </Button>
        </div>
      </div>

      {/* Test Input Forms */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-teal-400" />
            Test Parameters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {hypotheses.map((h, idx) => {
              const result = results[idx];
              return (
                <div
                  key={idx}
                  className="grid grid-cols-[1fr_100px_100px_80px_auto_auto] gap-2 items-center p-2 rounded bg-navy-900/50"
                >
                  <Input
                    value={h.name}
                    onChange={(e) => updateHypothesis(idx, "name", e.target.value)}
                    className="h-8 text-sm"
                    placeholder="Name"
                  />
                  <Input
                    value={h.computed}
                    onChange={(e) => updateHypothesis(idx, "computed", e.target.value)}
                    className="h-8 text-sm font-mono"
                    placeholder="Computed"
                  />
                  <Input
                    value={h.reference}
                    onChange={(e) => updateHypothesis(idx, "reference", e.target.value)}
                    className="h-8 text-sm font-mono"
                    placeholder="Reference"
                  />
                  <Input
                    value={h.tolerance}
                    onChange={(e) => updateHypothesis(idx, "tolerance", e.target.value)}
                    className="h-8 text-sm font-mono"
                    placeholder="Tol"
                  />
                  {result && (
                    <Badge
                      variant={result.passed ? "success" : "destructive"}
                      className="text-[10px]"
                    >
                      {result.passed ? "PASS" : "FAIL"} (ε={result.relativeError.toExponential(1)})
                    </Badge>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => removeHypothesis(idx)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {results.map((r, idx) => (
          <MetricCard
            key={idx}
            label={r.name}
            value={r.computed.toFixed(6)}
            deviation={r.deviation}
          />
        ))}
      </div>

      {/* Parameter Sweep */}
      <Card>
        <CardHeader>
          <CardTitle>Parameter Sweep Visualization</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="text-xs text-gray-400">Parameter</label>
              <select
                value={sweepParam}
                onChange={(e) => setSweepParam(e.target.value)}
                className="w-full h-8 rounded border border-navy-600 bg-navy-900 text-sm text-white px-2"
              >
                <option value="b_Ch">b_Ch</option>
                <option value="δ_C">δ_C</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400">Min</label>
              <Input
                value={sweepMin}
                onChange={(e) => setSweepMin(e.target.value)}
                className="h-8 text-sm font-mono"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400">Max</label>
              <Input
                value={sweepMax}
                onChange={(e) => setSweepMax(e.target.value)}
                className="h-8 text-sm font-mono"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400">Steps</label>
              <Input
                value={sweepSteps}
                onChange={(e) => setSweepSteps(e.target.value)}
                className="h-8 text-sm font-mono"
              />
            </div>
          </div>
          <LiveChart
            data={sweepData}
            xKey="x"
            lines={[
              { key: "Δ_{Ch}", color: "#8b5cf6", name: "Δ_{Ch}" },
              { key: "Reference", color: "#fbbf24", name: "Observed Δ = 3.443" },
            ]}
            type="line"
            height={300}
          />
        </CardContent>
      </Card>
    </div>
  );
}
