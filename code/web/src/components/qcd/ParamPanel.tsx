"use client";

/**
 * ParamPanel.tsx — Interactive parameter panel for custom mode.
 *
 * Inputs:
 *   • κ_T slider  (0 … 100, default 8.45)
 *   • N slider    (10 … 10000, default 28)
 *   • n_flavors   (1 … 12, default 6)
 *   • seed        (integer)
 *   • Section multi-select (checkboxes 1..9)
 *
 * Buttons:
 *   • Live preview (just updates the store — section components recompute)
 *   • Run via Python (POST /api/run) — sets the canonical QCDResult
 *   • Reset to defaults
 */

import { useState } from "react";
import { Loader2, Play, RefreshCw, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { useQCDStore } from "@/lib/qcd/configStore";
import { useTranslation } from "@/lib/qcd/i18n";
import { SECTIONS } from "@/lib/qcd/constants";
import type { QCDResult } from "@/lib/qcd/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";

export default function ParamPanel() {
  const { config, setConfig, toggleSection, resetConfig, setResult, runStatus, setRunStatus } = useQCDStore();
  const { t, lang } = useTranslation();
  const [busy, setBusy] = useState(false);

  const handleRunPython = async () => {
    setBusy(true);
    setRunStatus("running");
    toast.message(t("toast.runStart"));
    try {
      const body = JSON.stringify({ ...config, language: lang });
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
  };

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="text-base">{t("params.title")}</CardTitle>
        <CardDescription>
          <Badge variant="outline" className="mr-2">{t(`mode.${config.mode}`)}</Badge>
          <span className="text-xs text-muted-foreground">
            κ_T = {config.kappa_T_custom.toFixed(2)} · N = {config.N_custom} · n_f = {config.n_flavors} · seed = {config.seed}
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* κ_T */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="kappaT">{t("params.kappaT")}</Label>
            <Input
              id="kappaT"
              type="number"
              value={config.kappa_T_custom}
              min={0}
              max={100}
              step={0.05}
              onChange={(e) => setConfig({ kappa_T_custom: Math.max(0, Math.min(100, Number(e.target.value) || 0)) })}
              className="w-24 h-8 text-right"
            />
          </div>
          <Slider
            value={[config.kappa_T_custom]}
            min={0}
            max={100}
            step={0.05}
            onValueChange={(v) => setConfig({ kappa_T_custom: v[0] })}
            aria-label={t("params.kappaT")}
          />
        </div>

        {/* N */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="N">{t("params.N")}</Label>
            <Input
              id="N"
              type="number"
              value={config.N_custom}
              min={10}
              max={10000}
              step={1}
              onChange={(e) => setConfig({ N_custom: Math.max(10, Math.min(10000, Math.round(Number(e.target.value) || 28))) })}
              className="w-24 h-8 text-right"
            />
          </div>
          <Slider
            value={[Math.log10(config.N_custom)]}
            min={Math.log10(10)}
            max={Math.log10(10000)}
            step={0.01}
            onValueChange={(v) => setConfig({ N_custom: Math.round(Math.pow(10, v[0])) })}
            aria-label={t("params.N")}
          />
        </div>

        {/* n_flavors */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="nf">{t("params.nFlavors")}</Label>
            <Input
              id="nf"
              type="number"
              value={config.n_flavors}
              min={1}
              max={12}
              step={1}
              onChange={(e) => setConfig({ n_flavors: Math.max(1, Math.min(12, Math.round(Number(e.target.value) || 6))) })}
              className="w-24 h-8 text-right"
            />
          </div>
          <Slider
            value={[config.n_flavors]}
            min={1}
            max={12}
            step={1}
            onValueChange={(v) => setConfig({ n_flavors: v[0] })}
            aria-label={t("params.nFlavors")}
          />
        </div>

        {/* seed */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="seed">{t("params.seed")}</Label>
            <Input
              id="seed"
              type="number"
              value={config.seed}
              min={0}
              max={2 ** 31 - 1}
              step={1}
              onChange={(e) => setConfig({ seed: Math.max(0, Math.round(Number(e.target.value) || 0)) })}
              className="w-24 h-8 text-right"
            />
          </div>
        </div>

        {/* Sections */}
        <div className="space-y-2">
          <Label>{t("params.sections")}</Label>
          <div className="grid grid-cols-3 sm:grid-cols-3 gap-2">
            {SECTIONS.map((s) => {
              const checked = config.sections.includes(s.id);
              return (
                <label
                  key={s.id}
                  className="flex items-center gap-2 rounded-md border bg-card px-2 py-1.5 text-xs cursor-pointer hover:bg-muted"
                >
                  <Checkbox
                    checked={checked}
                    onCheckedChange={() => toggleSection(s.id)}
                    aria-label={`Section ${s.id}`}
                  />
                  <span className="font-medium">{s.id}</span>
                </label>
              );
            })}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2 pt-1">
          <Button onClick={handleRunPython} disabled={busy}>
            {busy ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {busy ? t("params.running") : t("params.runPython")}
          </Button>
          <Button variant="outline" onClick={() => toast.info(t("toast.preview"))}>
            <Sparkles className="h-4 w-4 mr-2" />
            {t("params.runLocal")}
          </Button>
          <Button variant="ghost" onClick={() => resetConfig()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            {t("params.reset")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
