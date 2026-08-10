"use client";

/**
 * DashboardView.tsx — Interactive dashboard with section-specific sliders
 * for all 9 sections of the Choptuik-QCD bridge.
 *
 * For each section the user gets:
 *   • A dedicated grid of sliders (κ_T, N, n_flavors, seed, … — section-dependent)
 *   • A live Plotly preview that re-renders on every slider move
 *   • Stat tiles summarizing key results
 *   • "Run via Python" button dispatching the canonical engine
 *
 * The dashboard reads/writes the shared Zustand configStore so that
 * changes here also propagate to the section detail views.
 *
 * Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7701)
 */

import { useEffect, useMemo, useState, useCallback } from "react";
import {
  Loader2, Play, RefreshCw, Sparkles, LayoutDashboard,
} from "lucide-react";
import { toast } from "sonner";
import { useQCDStore } from "@/lib/qcd/configStore";
import { useTranslation } from "@/lib/qcd/i18n";
import { SECTIONS, PALETTE } from "@/lib/qcd/constants";
import { buildSectionFigure, type SectionFigure } from "@/lib/qcd/figures";
import type { QCDResult } from "@/lib/qcd/types";
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import PlotlyChart from "./PlotlyChart";
import { cn } from "@/lib/utils";

/** Slider metadata for one section. */
interface SliderSpec {
  key: string;             // i18n key suffix (e.g. "kappaT" -> "dashboard.slider.kappaT")
  store: "kappa_T_custom" | "n_flavors" | "seed" | "N_custom" | "kappa_values";
  // For non-store-backed sliders we use a local override map
  localKey?: string;       // if set, value lives in localOverride state
  min: number;
  max: number;
  step: number;
  log?: boolean;           // log10 scale on slider; value stored linearly
  default: number;
  integer?: boolean;
}

/**
 * Per-section slider registry. Only sliders relevant to that section
 * are shown — keeps the dashboard compact and meaningful.
 */
const SECTION_SLIDERS: Record<number, SliderSpec[]> = {
  1: [ // O_chi eigvals
    { key: "kappaT", store: "kappa_T_custom", min: 0, max: 50, step: 0.05, default: 8.45 },
    { key: "nFlavors", store: "n_flavors", min: 1, max: 12, step: 1, default: 6, integer: true },
    { key: "seed", store: "seed", min: 0, max: 9999, step: 1, default: 42, integer: true },
  ],
  2: [ // RMT sweep
    { key: "kappaTmin", localKey: "kappaTmin", min: 0, max: 20, step: 0.1, default: 0.0 },
    { key: "kappaTmax", localKey: "kappaTmax", min: 0.5, max: 50, step: 0.1, default: 20.0 },
    { key: "nKappas", localKey: "nKappas", min: 5, max: 60, step: 1, default: 30, integer: true },
    { key: "seed", store: "seed", min: 0, max: 9999, step: 1, default: 42, integer: true },
    { key: "nBins", localKey: "nBins", min: 5, max: 40, step: 1, default: 20, integer: true },
  ],
  3: [ // K3 staircase
    { key: "Nstair", localKey: "Nstair", min: 4, max: 22, step: 1, default: 22, integer: true },
    { key: "seed", store: "seed", min: 0, max: 9999, step: 1, default: 42, integer: true },
  ],
  4: [ // N-scaling
    { key: "Nmin", localKey: "Nmin", min: 10, max: 500, step: 1, default: 20, integer: true },
    { key: "Nmax", localKey: "Nmax", min: 100, max: 10000, step: 1, default: 2000, integer: true },
    { key: "nPoints", localKey: "nPoints", min: 4, max: 30, step: 1, default: 12, integer: true },
    { key: "seed", store: "seed", min: 0, max: 9999, step: 1, default: 42, integer: true },
  ],
  5: [ // tau_relax
    { key: "theta0", localKey: "theta0", min: -20, max: -5, step: 0.5, default: -19 },
    { key: "tMinLog", localKey: "tMinLog", min: -50, max: -42, step: 0.5, default: -45 },
    { key: "tMaxLog", localKey: "tMaxLog", min: -42, max: -35, step: 0.5, default: -38 },
  ],
  6: [ // kappa_T physical
    { key: "deltaC", localKey: "deltaC", min: 0.05, max: 1.0, step: 0.005, default: Math.PI / 7 },
    { key: "lambdaQCD", localKey: "lambdaQCD", min: 0.05, max: 1.0, step: 0.01, default: 0.2 },
    { key: "kappaT", store: "kappa_T_custom", min: 0, max: 50, step: 0.05, default: 8.45 },
  ],
  7: [ // Cabibbo
    { key: "sin2Theta", localKey: "sin2Theta", min: 0.04, max: 0.06, step: 0.0005, default: 0.051 },
    { key: "deltaC", localKey: "deltaC", min: 0.05, max: 1.0, step: 0.005, default: Math.PI / 7 },
  ],
  8: [ // CP chain (no dynamic params — show a single "step reveal" slider)
    { key: "nKappas", localKey: "nStepsReveal", min: 1, max: 8, step: 1, default: 8, integer: true },
  ],
  9: [ // jet wake
    { key: "deltaC", localKey: "deltaC", min: 0.05, max: 1.0, step: 0.005, default: Math.PI / 7 },
    { key: "lambdaQCD", localKey: "lambdaQCD", min: 0.05, max: 1.0, step: 0.01, default: 0.2 },
    { key: "tMax", localKey: "tMax", min: 0.5, max: 4.0, step: 0.1, default: 2.0 },
  ],
};

/** Default local-override values (one set per section, merged on reset). */
const DEFAULT_LOCALS: Record<string, number> = {
  kappaTmin: 0.0, kappaTmax: 20.0, nKappas: 30, nBins: 20,
  Nstair: 22,
  Nmin: 20, Nmax: 2000, nPoints: 12,
  theta0: -19, tMinLog: -45, tMaxLog: -38,
  deltaC: Math.PI / 7, lambdaQCD: 0.2,
  sin2Theta: 0.051,
  nStepsReveal: 8, tMax: 2.0,
};

export default function DashboardView() {
  const { config, setConfig, setResult, runStatus, setRunStatus } = useQCDStore();
  const { t } = useTranslation();
  const [activeSection, setActiveSection] = useState<number>(1);
  const [localOverrides, setLocalOverrides] = useState<Record<string, number>>({ ...DEFAULT_LOCALS });
  const [busy, setBusy] = useState(false);
  const [liveCfg, setLiveCfg] = useState(config);   // local preview config (debounced)

  // Build effective config for live preview (merge store + locals)
  const effectiveCfg = useMemo(() => {
    // For sections 2 and 4 we override kappa_values / N_values from locals
    let kappa_values = config.kappa_values;
    let N_values = config.N_values;
    if (activeSection === 2) {
      const lo = localOverrides.kappaTmin ?? 0;
      const hi = localOverrides.kappaTmax ?? 20;
      const n = Math.max(2, Math.round(localOverrides.nKappas ?? 30));
      kappa_values = Array.from({ length: n }, (_, i) => lo + (hi - lo) * i / (n - 1));
    }
    if (activeSection === 4) {
      const lo = Math.max(10, Math.round(localOverrides.Nmin ?? 20));
      const hi = Math.max(lo + 1, Math.round(localOverrides.Nmax ?? 2000));
      const n = Math.max(3, Math.round(localOverrides.nPoints ?? 12));
      N_values = Array.from({ length: n }, (_, i) =>
        Math.round(Math.exp(Math.log(lo) + (Math.log(hi) - Math.log(lo)) * i / (n - 1)))
      );
    }
    return { ...config, kappa_values, N_values, sections: [activeSection] };
  }, [config, activeSection, localOverrides]);

  // Debounced live preview update on slider changes
  useEffect(() => {
    const id = setTimeout(() => setLiveCfg(effectiveCfg), 120);
    return () => clearTimeout(id);
  }, [effectiveCfg]);

  // Build the figure for the active section
  const figure: SectionFigure | null = useMemo(() => {
    try {
      return buildSectionFigure(activeSection, liveCfg);
    } catch (e) {
      console.error("[Dashboard] figure build failed", e);
      return null;
    }
  }, [activeSection, liveCfg]);

  /** Update a slider value — either in the store or local override. */
  const setSlider = useCallback((spec: SliderSpec, value: number) => {
    const v = spec.integer ? Math.round(value) : value;
    if (spec.localKey) {
      setLocalOverrides((s) => ({ ...s, [spec.localKey]: v }));
    } else if (spec.store) {
      setConfig({ [spec.store]: v } as Partial<typeof config>);
    }
  }, [setConfig, config]);

  /** Reset the active section's sliders to defaults. */
  const resetSection = useCallback(() => {
    const specs = SECTION_SLIDERS[activeSection] ?? [];
    const newLocals: Record<string, number> = { ...localOverrides };
    const newStorePatch: Record<string, number> = {};
    for (const s of specs) {
      if (s.localKey) {
        newLocals[s.localKey] = s.default;
      } else if (s.store) {
        newStorePatch[s.store] = s.default;
      }
    }
    setLocalOverrides(newLocals);
    if (Object.keys(newStorePatch).length > 0) {
      setConfig(newStorePatch as Partial<typeof config>);
    }
    toast.info(t("params.reset"));
  }, [activeSection, localOverrides, setConfig, t]);

  /** Run the canonical Python engine on the active section. */
  const handleRunPython = useCallback(async () => {
    setBusy(true);
    setRunStatus("running");
    toast.message(t("toast.runStart"));
    try {
      const body = JSON.stringify({ ...effectiveCfg, language: config.language });
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt);
      }
      const json = (await res.json()) as QCDResult;
      setResult(json);
      setRunStatus("ok");
      toast.success(t("toast.runOk", { elapsed: json.elapsed_s.toFixed(3) }));
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setRunStatus("error", msg);
      toast.error(t("toast.runErr", { msg }));
    } finally {
      setBusy(false);
    }
  }, [effectiveCfg, config.language, setResult, setRunStatus, t]);

  const specs = SECTION_SLIDERS[activeSection] ?? [];
  const stats = figure?.stats ?? [];

  return (
    <div className="space-y-4 p-4 md:p-6">
      {/* Header */}
      <Card className="shadow-sm" style={{ background: PALETTE.bg, borderColor: PALETTE.grid }}>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg flex items-center justify-center"
                 style={{ background: PALETTE.accent, color: "white" }}>
              <LayoutDashboard className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-xl">{t("dashboard.title")}</CardTitle>
              <CardDescription className="text-sm">{t("dashboard.subtitle")}</CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tabbed section selector */}
      <Tabs value={String(activeSection)} onValueChange={(v) => setActiveSection(Number(v))}>
        <TabsList className="flex flex-wrap h-auto gap-1 p-1 bg-card" style={{ borderColor: PALETTE.grid }}>
          {SECTIONS.map((s) => (
            <TabsTrigger
              key={s.id}
              value={String(s.id)}
              className={cn(
                "px-3 py-1.5 text-xs font-medium",
                activeSection === s.id ? "text-primary-foreground" : ""
              )}
            >
              <span className="mr-1.5">S{s.id}</span>
              <span className="hidden lg:inline">{t(`s${s.id}.short`)}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {SECTIONS.map((s) => (
          <TabsContent key={s.id} value={String(s.id)} className="mt-4">
            {s.id === activeSection && (
              <SectionDashboard
                sectionId={s.id}
                specs={specs}
                localOverrides={localOverrides}
                config={config}
                figure={figure}
                stats={stats}
                busy={busy}
                runStatus={runStatus}
                onSlider={setSlider}
                onReset={resetSection}
                onRunPython={handleRunPython}
              />
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}

/** One section's dashboard panel: sliders + chart + stats. */
interface SectionDashboardProps {
  sectionId: number;
  specs: SliderSpec[];
  localOverrides: Record<string, number>;
  config: ReturnType<typeof useQCDStore.getState>["config"];
  figure: SectionFigure | null;
  stats: SectionFigure["stats"];
  busy: boolean;
  runStatus: ReturnType<typeof useQCDStore.getState>["runStatus"];
  onSlider: (spec: SliderSpec, v: number) => void;
  onReset: () => void;
  onRunPython: () => void;
}

function SectionDashboard({
  sectionId, specs, localOverrides, config, figure, stats,
  busy, runStatus, onSlider, onReset, onRunPython,
}: SectionDashboardProps) {
  const { t } = useTranslation();

  /** Read the current value for a slider. */
  const readValue = (spec: SliderSpec): number => {
    if (spec.localKey) {
      return localOverrides[spec.localKey] ?? spec.default;
    }
    if (spec.store) {
      // @ts-expect-error dynamic key access
      return config[spec.store] ?? spec.default;
    }
    return spec.default;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
      {/* Left: sliders panel */}
      <Card className="lg:col-span-4 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center justify-between">
            <span>{t(`s${sectionId}.title`)}</span>
            <Badge variant="outline">{t("dashboard.tab")} {sectionId}</Badge>
          </CardTitle>
          <CardDescription className="text-xs">{t(`s${sectionId}.desc`)}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {specs.map((spec) => {
            const value = readValue(spec);
            const sliderValue = spec.log ? Math.log10(Math.max(1e-12, value)) : value;
            const minSlider = spec.log ? Math.log10(Math.max(1e-12, spec.min)) : spec.min;
            const maxSlider = spec.log ? Math.log10(Math.max(1e-12, spec.max)) : spec.max;
            return (
              <div key={spec.key} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <Label htmlFor={`s${sectionId}-${spec.key}`} className="text-xs">
                    {t(`dashboard.slider.${spec.key}`)}
                  </Label>
                  <Input
                    id={`s${sectionId}-${spec.key}`}
                    type="number"
                    value={value}
                    min={spec.min}
                    max={spec.max}
                    step={spec.step}
                    onChange={(e) => {
                      const v = Number(e.target.value);
                      if (!Number.isNaN(v)) onSlider(spec, v);
                    }}
                    className="w-28 h-7 text-right text-xs"
                  />
                </div>
                <Slider
                  value={[sliderValue]}
                  min={minSlider}
                  max={maxSlider}
                  step={spec.step}
                  onValueChange={(v) => onSlider(spec, spec.log ? Math.pow(10, v[0]) : v[0])}
                  aria-label={t(`dashboard.slider.${spec.key}`)}
                />
              </div>
            );
          })}

          {/* Action buttons */}
          <div className="flex flex-wrap gap-2 pt-2 border-t" style={{ borderColor: PALETTE.grid }}>
            <Button onClick={onRunPython} disabled={busy} size="sm">
              {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" /> : <Play className="h-3.5 w-3.5 mr-1.5" />}
              {busy ? t("params.running") : t("dashboard.runPython")}
            </Button>
            <Button variant="outline" size="sm" onClick={() => toast.info(t("toast.preview"))}>
              <Sparkles className="h-3.5 w-3.5 mr-1.5" />
              {t("dashboard.runLocal")}
            </Button>
            <Button variant="ghost" size="sm" onClick={onReset}>
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              {t("dashboard.reset")}
            </Button>
          </div>

          {/* Run status badge */}
          {runStatus !== "idle" && (
            <div className="pt-1">
              <Badge
                variant={runStatus === "ok" ? "default" : runStatus === "error" ? "destructive" : "secondary"}
                className="text-[10px]"
              >
                {runStatus}
              </Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Right: live Plotly chart + stats */}
      <Card className="lg:col-span-8 shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">{t(`s${sectionId}.title`)}</CardTitle>
          <CardDescription className="text-xs">{t("plot.loading")}</CardDescription>
        </CardHeader>
        <CardContent>
          {figure ? (
            <PlotlyChart figure={figure.figure} />
          ) : (
            <div className="flex items-center justify-center h-64 text-sm text-muted-foreground">
              {t("dashboard.noData")}
            </div>
          )}

          {/* Stat tiles */}
          {stats.length > 0 && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
              {stats.slice(0, 8).map((tile, i) => (
                <div
                  key={i}
                  className="rounded-md border p-2 text-xs"
                  style={{ borderColor: PALETTE.grid, background: PALETTE.bg }}
                >
                  <div className="text-muted-foreground truncate">
                    {t(`stats.${tile.label}`) ?? tile.label}
                  </div>
                  <div className="font-mono font-semibold truncate" style={{ color: PALETTE.primary }}>
                    {tile.value}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
