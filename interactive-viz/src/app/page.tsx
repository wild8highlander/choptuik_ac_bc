"use client";

import { MetricCard } from "@/components/metric-card";
import { VerificationStatus } from "@/components/verification-status";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { runVerification } from "@/lib/compute";
import { useEffect, useState } from "react";
import {
  PI,
  KLEIN_CURVE,
  SPINOR_PHASES,
  DIRAC_REFERENCE,
  CHOPTYUK_REFERENCE,
} from "@/lib/compute";
import { Activity, Sigma, Globe, Cpu } from "lucide-react";

export default function HomePage() {
  const [verifications, setVerifications] = useState<
    ReturnType<typeof runVerification>
  >([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVerifications(runVerification());
      setLoading(false);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  const passCount = verifications.filter((v) => v.passed).length;
  const totalTests = verifications.length;

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Choptyuk Spinor Monograph
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Spinor corrections <span className="font-mono text-teal-400">b-C</span> and{" "}
            <span className="font-mono text-teal-400">a-C</span> on the Klein quartic curve
          </p>
        </div>
        <Badge variant="outline" className="text-xs font-mono">
          PSL(2,7) · |Aut| = 168
        </Badge>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Genus"
          value={KLEIN_CURVE.genus.toString()}
          className="animate-count-up"
        />
        <MetricCard
          label="λ₁ (Klein)"
          value={KLEIN_CURVE.lambda1.toFixed(3)}
          deviation={Math.abs(KLEIN_CURVE.lambda1 - 3.838)}
          className="animate-count-up"
        />
        <MetricCard
          label="Δ_{bC}"
          value={DIRAC_REFERENCE.delta_bC.toFixed(6)}
          deviation={Math.abs(DIRAC_REFERENCE.delta_bC - 3.438710)}
          className="animate-count-up"
        />
        <MetricCard
          label="Δ_{Ch,full}"
          value={CHOPTYUK_REFERENCE.Delta_Ch_full.toFixed(6)}
          deviation={Math.abs(CHOPTYUK_REFERENCE.Delta_Ch_full - 3.447040)}
          className="animate-count-up"
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="δ_A = π/2"
          value={SPINOR_PHASES.delta_A.toFixed(6)}
          unit="rad"
        />
        <MetricCard
          label="δ_B = π/3"
          value={SPINOR_PHASES.delta_B.toFixed(6)}
          unit="rad"
        />
        <MetricCard
          label="δ_C = π/7"
          value={SPINOR_PHASES.delta_C.toFixed(6)}
          unit="rad"
        />
        <MetricCard
          label="b_Ch"
          value={CHOPTYUK_REFERENCE.b_Ch.toFixed(6)}
          deviation={Math.abs(CHOPTYUK_REFERENCE.b_Ch - 0.376510)}
        />
      </div>

      {/* Quick Verification Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-teal-400" />
            Quick Verification
            {loading ? (
              <Badge variant="secondary">Computing...</Badge>
            ) : (
              <Badge variant={passCount === totalTests ? "success" : "destructive"}>
                {passCount}/{totalTests} passed
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {verifications.map((v) => (
              <div
                key={v.id}
                className="flex items-center justify-between p-2 rounded bg-navy-900/50 animate-slide-up"
              >
                <span className="text-xs text-gray-400 font-mono">
                  {v.description}
                </span>
                <VerificationStatus
                  passed={v.passed}
                  relativeError={v.relativeError}
                />
              </div>
            ))}
            {loading &&
              Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={`skel-${i}`}
                  className="h-8 bg-navy-800 rounded animate-pulse-glow"
                />
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Summary Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="h-4 w-4 text-cyan-400" />
              Klein Curve
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Genus</span>
              <span className="font-mono text-white">{KLEIN_CURVE.genus}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">|Aut|</span>
              <span className="font-mono text-white">{KLEIN_CURVE.automorphismOrder}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">λ₁</span>
              <span className="font-mono text-teal-400">{KLEIN_CURVE.lambda1}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">R</span>
              <span className="font-mono text-white">{KLEIN_CURVE.R}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Sigma className="h-4 w-4 text-science-violet" />
              Spinor Phases
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">δ_A</span>
              <span className="font-mono text-teal-400">{SPINOR_PHASES.delta_A.toFixed(6)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">δ_B</span>
              <span className="font-mono text-teal-400">{SPINOR_PHASES.delta_B.toFixed(6)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">δ_C</span>
              <span className="font-mono text-teal-400">{SPINOR_PHASES.delta_C.toFixed(6)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Sum</span>
              <span className="font-mono text-white">
                {(SPINOR_PHASES.delta_A + SPINOR_PHASES.delta_B + SPINOR_PHASES.delta_C).toFixed(6)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Globe className="h-4 w-4 text-science-gold" />
              Choptyuk Invariants
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Δ_{'{'}Ch,base{'}'}</span>
              <span className="font-mono text-teal-400">{CHOPTYUK_REFERENCE.Delta_Ch_base.toFixed(6)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Δ_{'{'}Ch,full{'}'}</span>
              <span className="font-mono text-teal-400">{CHOPTYUK_REFERENCE.Delta_Ch_full.toFixed(6)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">b_Ch</span>
              <span className="font-mono text-white">{CHOPTYUK_REFERENCE.b_Ch.toFixed(6)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Observed Δ</span>
              <span className="font-mono text-science-gold">{CHOPTYUK_REFERENCE.observed_Delta.toFixed(3)}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
