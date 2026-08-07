"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LiveChart } from "@/components/live-chart";
import { MetricCard } from "@/components/metric-card";
import { GW_EVENTS, detectorSensitivity, CHOPTYUK_REFERENCE } from "@/lib/compute";
import { useMemo } from "react";
import { Radio, Satellite, Clock } from "lucide-react";

export default function QNMPage() {
  // Frequency comparison chart data
  const freqData = useMemo(
    () =>
      GW_EVENTS.map((ev) => ({
        name: ev.name,
        "f_QNM (Hz)": ev.qnmFrequency,
        "M_f (M☉)": ev.finalMass,
        SNR: ev.snr,
      })),
    []
  );

  // Detector sensitivity curve
  const sensitivityData = useMemo(() => {
    const freqs: number[] = [];
    for (let f = 10; f <= 500; f += 5) freqs.push(f);
    return freqs.map((f) => ({
      freq: f,
      LIGO: Math.log10(detectorSensitivity(f, "LIGO")),
      Virgo: Math.log10(detectorSensitivity(f, "Virgo")),
      ET: Math.log10(detectorSensitivity(f, "ET")),
    }));
  }, []);

  // Future detectability projections
  const futureData = useMemo(() => {
    const years = [2025, 2030, 2035, 2040, 2045, 2050];
    return years.map((year) => ({
      year,
      "LIGO A+": 1 - Math.exp(-0.02 * (year - 2020)),
      "ET Design": 1 - Math.exp(-0.08 * (year - 2025)),
      "CE (3G)": 1 - Math.exp(-0.12 * (year - 2030)),
    }));
  }, []);

  return (
    <div className="space-y-6 animate-slide-up">
      <div>
        <h1 className="text-2xl font-bold text-white">QNM / LIGO Predictions</h1>
        <p className="text-sm text-gray-400 mt-1">
          Quasinormal mode predictions from Choptyuk invariants for LIGO/Virgo events
        </p>
      </div>

      {/* GW Event Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {GW_EVENTS.map((ev) => (
          <Card key={ev.name} className="hover:border-teal-500/30 transition-all">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Radio className="h-5 w-5 text-science-gold" />
                {ev.name}
                <Badge variant="outline" className="text-[10px] font-mono">
                  {ev.date}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-gray-400">m₁, m₂</p>
                  <p className="font-mono text-white">
                    {ev.masses[0]}, {ev.masses[1]} M☉
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">M_f</p>
                  <p className="font-mono text-teal-400">{ev.finalMass} M☉</p>
                </div>
                <div>
                  <p className="text-gray-400">a_f</p>
                  <p className="font-mono text-white">{ev.spin}</p>
                </div>
                <div>
                  <p className="text-gray-400">M_chirp</p>
                  <p className="font-mono text-white">{ev.chirpMass} M☉</p>
                </div>
                <div>
                  <p className="text-gray-400">f_QNM</p>
                  <p className="font-mono text-science-gold">
                    {ev.qnmFrequency} Hz
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">τ_damp</p>
                  <p className="font-mono text-white">
                    {ev.qnmDamping} ms
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">SNR</p>
                  <p className="font-mono text-cyan-400">{ev.snr}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Choptyuk Correction */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          label="Δ_{Ch,full}"
          value={CHOPTYUK_REFERENCE.Delta_Ch_full.toFixed(6)}
          deviation={CHOPTYUK_REFERENCE.deviation}
        />
        <MetricCard
          label="QNM Correction Factor"
          value={(1 + 0.001 * CHOPTYUK_REFERENCE.Delta_Ch_full).toFixed(6)}
        />
        <MetricCard
          label="b_Ch"
          value={CHOPTYUK_REFERENCE.b_Ch.toFixed(6)}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Satellite className="h-5 w-5 text-cyan-400" />
              QNM Frequency Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <LiveChart
              data={freqData}
              xKey="name"
              lines={[
                { key: "f_QNM (Hz)", color: "#fbbf24", name: "f_QNM (Hz)" },
                { key: "SNR", color: "#06b6d4", name: "SNR" },
              ]}
              type="bar"
              height={300}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Detector Sensitivity (log₁₀ strain/√Hz)</CardTitle>
          </CardHeader>
          <CardContent>
            <LiveChart
              data={sensitivityData}
              xKey="freq"
              lines={[
                { key: "LIGO", color: "#14b8a6", name: "LIGO" },
                { key: "Virgo", color: "#f43f5e", name: "Virgo" },
                { key: "ET", color: "#8b5cf6", name: "Einstein Telescope" },
              ]}
              type="line"
              height={300}
            />
          </CardContent>
        </Card>
      </div>

      {/* Future Detectability */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-science-emerald" />
            Future Detectability Projections
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LiveChart
            data={futureData}
            xKey="year"
            lines={[
              { key: "LIGO A+", color: "#14b8a6", name: "LIGO A+" },
              { key: "ET Design", color: "#8b5cf6", name: "Einstein Telescope" },
              { key: "CE (3G)", color: "#fbbf24", name: "Cosmic Explorer" },
            ]}
            type="line"
            height={300}
          />
          <p className="text-xs text-gray-500 mt-2">
            Probability of detecting Choptyuk-corrected QNM signature over time for next-generation detectors.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
