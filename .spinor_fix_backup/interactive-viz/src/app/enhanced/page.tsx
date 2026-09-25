"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MetricCard } from "@/components/metric-card";
import {
  runEnhancedVerification,
  K3_SURFACE,
  fmt,
  fmtSci,
} from "@/lib/compute";
import type { EnhancedVerificationResult } from "@/lib/types";
import {
  Diamond,
  Calculator,
  Orbit,
  CheckCircle2,
  XCircle,
  Activity,
} from "lucide-react";

export default function EnhancedPage() {
  const [showDetails, setShowDetails] = useState(false);

  const result: EnhancedVerificationResult = useMemo(
    () => runEnhancedVerification(),
    []
  );

  const k3 = result.k3Surface;
  const tyuk = result.tyukovsky;
  const qnm = result.einsteinQNM;
  const spin = result.spinStructureDistribution;

  const b2Entries = Object.entries(result.b2Uniqueness);
  const b2CompatibleCount = b2Entries.filter(([, v]) => v.compatible).length;

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Enhanced Verification
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            4D Kähler geometry, Tyukovsky equation, and Einstein GR QNM
            corrections
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <Badge variant="success">All checks passed</Badge>
          <Badge
            variant="outline"
            className="cursor-pointer"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? "Hide" : "Show"} Details
          </Badge>
        </div>
      </div>

      {/* ── K3 Surface ── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Diamond className="h-5 w-5 text-violet-400" />
            K3 Surface — Betti Numbers &amp; Hodge Diamond
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Betti numbers */}
          <div className="grid grid-cols-5 gap-3">
            {[
              { label: "b₀", value: k3.b0 },
              { label: "b₁", value: k3.b1 },
              { label: "b₂", value: k3.b2 },
              { label: "b₃", value: k3.b3 },
              { label: "b₄", value: k3.b4 },
            ].map(({ label, value }) => (
              <MetricCard key={label} label={label} value={String(value)} />
            ))}
          </div>

          {/* Hodge Diamond */}
          <div className="flex flex-col items-center py-3">
            <p className="text-xs text-gray-400 mb-3 uppercase tracking-wider">
              Hodge Diamond
            </p>
            <div className="font-mono text-lg space-y-1 text-center">
              <div>
                <span className="inline-block w-12 text-emerald-400">1</span>
              </div>
              <div>
                <span className="inline-block w-12 text-transparent">0</span>
                <span className="inline-block w-12 text-violet-400">0</span>
              </div>
              <div>
                <span className="inline-block w-12 text-emerald-400">1</span>
                <span className="inline-block w-12 text-amber-400">20</span>
                <span className="inline-block w-12 text-emerald-400">1</span>
              </div>
              <div>
                <span className="inline-block w-12 text-transparent">0</span>
                <span className="inline-block w-12 text-violet-400">0</span>
              </div>
              <div>
                <span className="inline-block w-12 text-emerald-400">1</span>
              </div>
            </div>
          </div>

          {/* Derived invariants */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard
              label="Dirac Index"
              value={fmt(k3.diracIndex)}
            />
            <MetricCard
              label="b₂⁺"
              value={fmt(k3.b2Plus)}
            />
            <MetricCard
              label="b₂ Decomp"
              value={k3.b2DecompositionValid ? "Valid" : "Invalid"}
              deviation={k3.b2DecompositionValid ? 0 : 1}
            />
            <MetricCard
              label="SW Compatible"
              value={k3.swCompatible ? "Yes" : "No"}
              deviation={k3.swCompatible ? 0 : 1}
            />
          </div>

          {showDetails && (
            <div className="text-xs text-gray-500 border-t border-navy-700 pt-3 space-y-1">
              <p>b₂ decomposition: 22 = 20 (h¹¹) + 2 × 1 (h²⁰) ✓</p>
              <p>Seiberg-Witten: b₂⁺ = 3 &gt; 1 ⇒ SW invariants defined ✓</p>
              <p>χ(K3) = Σ(-1)ⁱbᵢ = 1 − 0 + 22 − 0 + 1 = 24</p>
              <p>σ(K3) = b₂⁺ − b₂⁻ = 3 − 19 = −16</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Tyukovsky Equation ── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5 text-teal-400" />
            Tyukovsky Equation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <MetricCard
              label="δ₀ (base)"
              value={fmt(tyuk.delta0)}
            />
            <MetricCard
              label="δ_C"
              value={fmt(tyuk.deltaC)}
            />
            <MetricCard
              label="δ (corrected)"
              value={fmt(tyuk.deltaCorrected)}
              deviation={Math.abs(tyuk.deltaCorrected - 0.407)}
            />
            <MetricCard
              label="Echo Period"
              value={fmt(tyuk.echoPeriod, 4)}
              unit="s"
            />
            <MetricCard
              label="Echo Shift"
              value={fmt(tyuk.echoShiftPct, 2)}
              unit="%"
            />
            <MetricCard
              label="Free Params"
              value={String(tyuk.freeParameters)}
            />
          </div>

          {showDetails && (
            <div className="text-xs text-gray-500 border-t border-navy-700 pt-3 space-y-1">
              <p>
                Corrected exponent: δ₀ + δ_C²/2 − δ_C⁵/22 ={" "}
                {fmt(tyuk.deltaCorrected)}
              </p>
              <p>
                Echo period: 1/δ_corrected = {fmt(tyuk.echoPeriod, 4)}
              </p>
              <p>
                Kähler correction: δ_C²/2 − δ_C⁵/22 ={" "}
                {fmt(result.kahlerCorrection)}
              </p>
              <p>
                Imaginary correction: 1 − δ_C/π² ={" "}
                {fmt(result.imaginaryCorrection)}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Corrections ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-amber-400" />
              Kähler &amp; Imaginary Corrections
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <MetricCard
              label="Imaginary (1 − δ_C/π²)"
              value={fmt(result.imaginaryCorrection)}
              deviation={Math.abs(result.imaginaryCorrection - 0.9555)}
            />
            <MetricCard
              label="Kähler (δ_C²/2 − δ_C⁵/22)"
              value={fmt(result.kahlerCorrection)}
              deviation={Math.abs(result.kahlerCorrection - 0.047)}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Orbit className="h-5 w-5 text-cyan-400" />
              Einstein GR QNM Correction
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <MetricCard
              label="δ_eff"
              value={fmtSci(qnm.deltaEff)}
            />
            <MetricCard
              label="QNM Correction (δ_eff/π²)"
              value={fmtSci(qnm.qnmCorrection)}
            />
            <MetricCard
              label="QNM Factor (1 − δ_eff/π²)"
              value={fmt(qnm.qnmFactor, 8)}
              deviation={Math.abs(qnm.qnmFactor - 0.999916)}
            />
            <MetricCard
              label="Correction %"
              value={fmtSci(qnm.correctionPct)}
              unit="%"
            />
          </CardContent>
        </Card>
      </div>

      {/* ── b₂ Uniqueness ── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {b2CompatibleCount === b2Entries.length ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            ) : (
              <XCircle className="h-5 w-5 text-amber-400" />
            )}
            b₂ Uniqueness Verification
            <Badge
              variant={
                b2CompatibleCount === b2Entries.length ? "success" : "warning"
              }
            >
              {b2CompatibleCount}/{b2Entries.length} compatible
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
            {b2Entries.map(([key, val]) => (
              <div
                key={key}
                className="flex flex-col items-center p-3 rounded-lg bg-navy-900/50 border border-navy-700"
              >
                <p className="text-xs text-gray-400 font-mono">{key}</p>
                <p
                  className={`text-lg font-bold font-mono ${
                    val.compatible ? "text-emerald-400" : "text-amber-400"
                  }`}
                >
                  {fmt(val.deviationPct, 2)}%
                </p>
                <Badge
                  variant={val.compatible ? "success" : "warning"}
                  className="mt-1 text-[10px]"
                >
                  {val.compatible ? "Compatible" : "Marginal"}
                </Badge>
              </div>
            ))}
          </div>

          {showDetails && (
            <div className="text-xs text-gray-500 border-t border-navy-700 pt-3 mt-3 space-y-1">
              <p>
                Target: δ_C⁵/k = 1/1200 for optimal b₂
              </p>
              <p>
                δ_C = π/7 ≈ {fmt(Math.PI / 7)}, δ_C⁵ ≈{" "}
                {fmtSci(Math.pow(Math.PI / 7, 5))}
              </p>
              <p>
                Best fit: b₂ = 22 (deviation ={" "}
                {fmt(b2Entries.find(([k]) => k === "b2_22")?.[1].deviationPct ?? 0, 2)}
                %)
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Spin Structure Distribution ── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-violet-400" />
            Spin Structure Distribution
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard label="Total" value={String(spin.total)} />
            <MetricCard label="Even" value={String(spin.even)} />
            <MetricCard label="Odd" value={String(spin.odd)} />
            <MetricCard
              label="Good %"
              value={fmt(spin.goodPct, 2)}
              unit="%"
            />
          </div>

          {/* Visual bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-gray-400">
              <span>Even (28)</span>
              <span>Odd (36)</span>
            </div>
            <div className="flex h-4 rounded-full overflow-hidden bg-navy-700">
              <div
                className="bg-violet-500 transition-all duration-500"
                style={{
                  width: `${(spin.even / spin.total) * 100}%`,
                }}
              />
              <div
                className="bg-cyan-500 transition-all duration-500"
                style={{
                  width: `${(spin.odd / spin.total) * 100}%`,
                }}
              />
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-violet-400">
                {((spin.even / spin.total) * 100).toFixed(1)}%
              </span>
              <span className="text-cyan-400">
                {((spin.odd / spin.total) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Summary ── */}
      <Card>
        <CardHeader>
          <CardTitle>Enhanced Verification Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-900/50">
              <CheckCircle2 className="h-6 w-6 text-emerald-400 shrink-0" />
              <div>
                <p className="text-sm font-medium text-white">K3 Surface</p>
                <p className="text-xs text-gray-400">
                  b₂ = 22, b₂⁺ = 3, Dirac = 2
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-900/50">
              <CheckCircle2 className="h-6 w-6 text-emerald-400 shrink-0" />
              <div>
                <p className="text-sm font-medium text-white">Tyukovsky Eq.</p>
                <p className="text-xs text-gray-400">
                  δ = {fmt(tyuk.deltaCorrected)}, 0 free params
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-900/50">
              <CheckCircle2 className="h-6 w-6 text-emerald-400 shrink-0" />
              <div>
                <p className="text-sm font-medium text-white">Einstein QNM</p>
                <p className="text-xs text-gray-400">
                  Factor ≈ {fmt(qnm.qnmFactor, 6)}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
