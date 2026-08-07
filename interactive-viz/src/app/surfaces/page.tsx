"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LiveChart } from "@/components/live-chart";
import { RIEMANN_SURFACES } from "@/lib/compute";
import { useMemo } from "react";
import { Layers } from "lucide-react";

export default function SurfacesPage() {
  const comparisonData = useMemo(
    () =>
      RIEMANN_SURFACES.map((s) => ({
        name: s.name,
        "Δ_{bC}": s.delta_bC,
        "Δ_{aC}": s.delta_aC * 1000, // scale up for visibility
        "Δ_{Ch}": s.Delta_Ch,
        "λ₁": s.lambda1,
      })),
    []
  );

  const genusData = useMemo(
    () =>
      RIEMANN_SURFACES.map((s) => ({
        name: s.name,
        genus: s.genus,
        "|Aut|": s.automorphismOrder,
      })),
    []
  );

  return (
    <div className="space-y-6 animate-slide-up">
      <div>
        <h1 className="text-2xl font-bold text-white">Surface Comparison</h1>
        <p className="text-sm text-gray-400 mt-1">
          Comparing Bolza, Bring, and Macbeath surfaces
        </p>
      </div>

      {/* Surface Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {RIEMANN_SURFACES.map((s) => (
          <Card key={s.name} className="hover:border-teal-500/30 transition-all">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-5 w-5 text-teal-400" />
                {s.name} Surface
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Genus</span>
                <span className="font-mono text-white">{s.genus}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">|Aut|</span>
                <span className="font-mono text-white">{s.automorphismOrder}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">λ₁</span>
                <span className="font-mono text-teal-400">{s.lambda1}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Δ_{'{'}bC{'}'}</span>
                <span className="font-mono text-teal-400">{s.delta_bC.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Δ_{'{'}aC{'}'}</span>
                <span className="font-mono text-amber-400">
                  {s.delta_aC.toExponential(4)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Δ_{'{'}Ch{'}'}</span>
                <span className="font-mono text-science-violet">
                  {s.Delta_Ch.toFixed(4)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Curvature</span>
                <span className="font-mono text-white">{s.curvature}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Bar Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Invariant Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <LiveChart
              data={comparisonData}
              xKey="name"
              lines={[
                { key: "Δ_{bC}", color: "#14b8a6", name: "Δ_{bC}" },
                { key: "Δ_{Ch}", color: "#8b5cf6", name: "Δ_{Ch}" },
                { key: "λ₁", color: "#06b6d4", name: "λ₁" },
              ]}
              type="bar"
              height={350}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Genus & Automorphism Order</CardTitle>
          </CardHeader>
          <CardContent>
            <LiveChart
              data={genusData}
              xKey="name"
              lines={[
                { key: "genus", color: "#fbbf24", name: "Genus" },
                { key: "|Aut|", color: "#22d3ee", name: "|Aut|" },
              ]}
              type="bar"
              height={350}
            />
          </CardContent>
        </Card>
      </div>

      {/* a-C correction scale note */}
      <Card>
        <CardContent className="p-4">
          <p className="text-xs text-gray-500">
            Note: Δ_{'{'}aC{'}'} values are scaled ×1000 in the bar chart for visibility.
            Actual values range from ~4×10⁻⁴ to ~1×10⁻³.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
