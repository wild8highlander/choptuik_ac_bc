"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ParameterSlider } from "@/components/parameter-slider";
import { LiveChart } from "@/components/live-chart";
import { MetricCard } from "@/components/metric-card";
import { computeFull, fmt } from "@/lib/compute";
import {
  DEFAULT_PARAMS,
  sweepDeltaC,
  sweepLambda1,
  sweepBCh,
  sweepR,
  computeConvergence,
} from "@/lib/simulation";
import type { SimulationParams } from "@/lib/types";
import { SlidersHorizontal, TrendingUp, BarChart3 } from "lucide-react";

export default function SimulatePage() {
  const [params, setParams] = useState<SimulationParams>({ ...DEFAULT_PARAMS });

  const updateParam = (key: keyof SimulationParams, value: number) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  // Real-time computation
  const computed = useMemo(() => computeFull(params), [params]);

  // Parameter sweeps (recomputed when params change)
  const sweepDC = useMemo(() => sweepDeltaC(params), [params]);
  const sweepL1 = useMemo(() => sweepLambda1(params), [params]);
  const sweepB = useMemo(() => sweepBCh(params), [params]);
  const sweepRv = useMemo(() => sweepR(params), [params]);

  // Convergence analysis
  const convergence = useMemo(() => computeConvergence(params), [params]);

  // Chart data
  const sweepDCData = useMemo(
    () =>
      sweepDC.values.map((v, i) => ({
        x: v.toFixed(3),
        "Δ_{bC}": sweepDC.delta_bC[i],
        "Δ_{aC}": sweepDC.delta_aC[i],
        "Δ_{Ch}": sweepDC.Delta_Ch[i],
        Observed: sweepDC.observed[i],
      })),
    [sweepDC]
  );

  const sweepL1Data = useMemo(
    () =>
      sweepL1.values.map((v, i) => ({
        x: v.toFixed(2),
        "Δ_{bC}": sweepL1.delta_bC[i],
        "Δ_{Ch}": sweepL1.Delta_Ch[i],
        Observed: sweepL1.observed[i],
      })),
    [sweepL1]
  );

  const sweepBData = useMemo(
    () =>
      sweepB.values.map((v, i) => ({
        x: v.toFixed(3),
        "Δ_{Ch}": sweepB.Delta_Ch[i],
        Observed: sweepB.observed[i],
      })),
    [sweepB]
  );

  const convergenceData = useMemo(
    () =>
      convergence.terms.map((n, i) => ({
        n,
        "S_n": convergence.partialSums[i],
      })),
    [convergence]
  );

  const deviation = Math.abs(computed.chFull - 3.443);

  return (
    <div className="space-y-6 animate-slide-up">
      <div>
        <h1 className="text-2xl font-bold text-white">Simulation</h1>
        <p className="text-sm text-gray-400 mt-1">
          Interactive parameter sweeps with real-time chart updates
        </p>
      </div>

      {/* Current Computed Values */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <MetricCard label="δ_A" value={fmt(computed.deltaA, 4)} unit="rad" />
        <MetricCard label="δ_B" value={fmt(computed.deltaB, 4)} unit="rad" />
        <MetricCard label="δ_C" value={fmt(computed.deltaC, 4)} unit="rad" />
        <MetricCard label="λ_{D²}" value={fmt(computed.lambdaTriv, 4)} />
        <MetricCard label="Δ_{bC}" value={fmt(computed.dBC, 4)} />
        <MetricCard label="Δ_{Ch}" value={fmt(computed.chFull, 4)} deviation={deviation} />
        <MetricCard
          label="Deviation"
          value={deviation.toExponential(3)}
          className={deviation < 0.01 ? "border-emerald-500/30" : "border-amber-500/30"}
        />
      </div>

      {/* Parameter Sliders */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SlidersHorizontal className="h-5 w-5 text-teal-400" />
            Parameters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ParameterSlider
              label="Spinor phase C"
              symbol="δ_C"
              value={params.delta_C}
              min={0.1}
              max={1.5}
              step={0.001}
              onChange={(v) => updateParam("delta_C", v)}
            />
            <ParameterSlider
              label="First eigenvalue"
              symbol="λ₁"
              value={params.lambda_1}
              min={2.0}
              max={6.0}
              step={0.01}
              onChange={(v) => updateParam("lambda_1", v)}
            />
            <ParameterSlider
              label="Structure index"
              symbol="k"
              value={params.k_struct}
              min={0}
              max={63}
              step={1}
              onChange={(v) => updateParam("k_struct", v)}
              formatValue={(v) => v.toFixed(0)}
            />
            <ParameterSlider
              label="Scalar curvature"
              symbol="R"
              value={params.R}
              min={-5}
              max={-0.1}
              step={0.01}
              onChange={(v) => updateParam("R", v)}
            />
            <ParameterSlider
              label="Genus"
              symbol="g"
              value={params.genus}
              min={2}
              max={7}
              step={1}
              onChange={(v) => updateParam("genus", v)}
              formatValue={(v) => v.toFixed(0)}
            />
            <ParameterSlider
              label="Choptyuk parameter"
              symbol="b_Ch"
              value={params.b_Ch}
              min={0}
              max={1}
              step={0.001}
              onChange={(v) => updateParam("b_Ch", v)}
            />
            <ParameterSlider
              label="c4 coefficient"
              symbol="c₄"
              value={params.c4}
              min={0}
              max={2}
              step={0.01}
              onChange={(v) => updateParam("c4", v)}
            />
            <ParameterSlider
              label="c6 coefficient"
              symbol="c₆"
              value={params.c6}
              min={0}
              max={2}
              step={0.01}
              onChange={(v) => updateParam("c6", v)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Sweep Charts */}
      <Tabs defaultValue="deltaC" className="w-full">
        <TabsList>
          <TabsTrigger value="deltaC">δ_C Sweep</TabsTrigger>
          <TabsTrigger value="lambda1">λ₁ Sweep</TabsTrigger>
          <TabsTrigger value="bCh">b_Ch Sweep</TabsTrigger>
          <TabsTrigger value="R">R Sweep</TabsTrigger>
          <TabsTrigger value="convergence">Convergence</TabsTrigger>
        </TabsList>

        <TabsContent value="deltaC">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-teal-400" />
                δ_C Parameter Sweep
              </CardTitle>
            </CardHeader>
            <CardContent>
              <LiveChart
                data={sweepDCData}
                xKey="x"
                lines={[
                  { key: "Δ_{bC}", color: "#14b8a6", name: "Δ_{bC}" },
                  { key: "Δ_{Ch}", color: "#8b5cf6", name: "Δ_{Ch}" },
                  { key: "Observed", color: "#fbbf24", name: "Observed Δ" },
                ]}
                type="line"
                height={350}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="lambda1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-cyan-400" />
                λ₁ Parameter Sweep
              </CardTitle>
            </CardHeader>
            <CardContent>
              <LiveChart
                data={sweepL1Data}
                xKey="x"
                lines={[
                  { key: "Δ_{bC}", color: "#14b8a6", name: "Δ_{bC}" },
                  { key: "Δ_{Ch}", color: "#8b5cf6", name: "Δ_{Ch}" },
                  { key: "Observed", color: "#fbbf24", name: "Observed Δ" },
                ]}
                type="line"
                height={350}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bCh">
          <Card>
            <CardHeader>
              <CardTitle>b_Ch Parameter Sweep</CardTitle>
            </CardHeader>
            <CardContent>
              <LiveChart
                data={sweepBData}
                xKey="x"
                lines={[
                  { key: "Δ_{Ch}", color: "#8b5cf6", name: "Δ_{Ch}" },
                  { key: "Observed", color: "#fbbf24", name: "Observed Δ" },
                ]}
                type="area"
                height={350}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="R">
          <Card>
            <CardHeader>
              <CardTitle>R (Scalar Curvature) Sweep</CardTitle>
            </CardHeader>
            <CardContent>
              <LiveChart
                data={sweepRv.values.map((v, i) => ({
                  x: v.toFixed(2),
                  "Δ_{bC}": sweepRv.delta_bC[i],
                  "Δ_{Ch}": sweepRv.Delta_Ch[i],
                  Observed: sweepRv.observed[i],
                }))}
                xKey="x"
                lines={[
                  { key: "Δ_{bC}", color: "#14b8a6", name: "Δ_{bC}" },
                  { key: "Δ_{Ch}", color: "#8b5cf6", name: "Δ_{Ch}" },
                  { key: "Observed", color: "#fbbf24", name: "Observed Δ" },
                ]}
                type="line"
                height={350}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="convergence">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-science-violet" />
                Series Convergence Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <MetricCard
                  label="Limit"
                  value={fmt(convergence.limit, 6)}
                />
                <MetricCard
                  label="Convergence Rate"
                  value={convergence.convergenceRate.toExponential(4)}
                />
              </div>
              <LiveChart
                data={convergenceData}
                xKey="n"
                lines={[
                  { key: "S_n", color: "#14b8a6", name: "Partial Sum S_n" },
                ]}
                type="line"
                height={350}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
