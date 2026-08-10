"use client";

/**
 * ReportPanel.tsx — Report download panel.
 *
 * Each button POSTs the current config (and last result, if any) to
 * `/api/report?format=...` which dispatches the Python `report_engine.py`
 * to produce the requested file in /choptuik_ac_bc/code/web/output/.
 * The frontend then triggers a download via a hidden anchor.
 */

import { useState } from "react";
import { Download, FileText, Loader2 } from "lucide-react";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useQCDStore } from "@/lib/qcd/configStore";
import { useTranslation } from "@/lib/qcd/i18n";
import type { ReportFormat } from "@/lib/qcd/types";

const FORMATS: ReportFormat[] = ["txt", "csv", "md", "pdf", "html", "docx", "json"];

export default function ReportPanel() {
  const { config, result } = useQCDStore();
  const { t, lang } = useTranslation();
  const [busy, setBusy] = useState<ReportFormat | null>(null);
  const [paths, setPaths] = useState<Partial<Record<ReportFormat, string>>>({});

  const handleGenerate = async (fmt: ReportFormat) => {
    setBusy(fmt);
    try {
      const body = JSON.stringify({ ...config, language: lang, format: fmt });
      const res = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt);
      }
      const json = (await res.json()) as { path: string; download_url: string };
      setPaths((p) => ({ ...p, [fmt]: json.path }));
      // Trigger the download via a hidden anchor.
      const a = document.createElement("a");
      a.href = json.download_url;
      a.download = json.path.split("/").pop() ?? `report.${fmt}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      toast.success(t("toast.reportOk", { fmt: fmt.toUpperCase() }));
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      toast.error(t("toast.reportErr", { fmt: fmt.toUpperCase(), msg }));
    } finally {
      setBusy(null);
    }
  };

  const copyPath = async (p?: string) => {
    if (!p) return;
    try {
      await navigator.clipboard.writeText(p);
      toast.success(t("toast.copied"));
    } catch {
      /* ignore */
    }
  };

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <FileText className="h-4 w-4" />
          {t("report.title")}
        </CardTitle>
        <CardDescription>{t("report.intro")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {result ? (
          <div className="text-xs text-muted-foreground">
            {t("report.lastRun")}:{" "}
            <span className="font-mono text-foreground">
              {result.timestamp} · {result.elapsed_s.toFixed(3)}s · sections {result.sections_run.join(",")}
            </span>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground italic">{t("report.noRun")}</div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
          {FORMATS.map((fmt) => (
            <Button
              key={fmt}
              variant="outline"
              onClick={() => handleGenerate(fmt)}
              disabled={busy !== null}
              className="h-auto py-2 flex flex-col gap-1"
            >
              {busy === fmt ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              <span className="text-xs">{t(`report.fmt.${fmt}`)}</span>
            </Button>
          ))}
        </div>

        {Object.keys(paths).length > 0 && (
          <div className="rounded-md border bg-muted/40 p-3 space-y-1">
            <div className="text-[10px] uppercase tracking-wide text-muted-foreground">
              {t("report.lastRun")} — saved paths
            </div>
            {Object.entries(paths).map(([fmt, p]) => (
              <div key={fmt} className="flex items-center justify-between gap-2 text-xs font-mono">
                <span className="truncate flex-1" title={p}>{p}</span>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 px-2 text-[10px]"
                  onClick={() => copyPath(p)}
                >
                  {t("report.copyPath")}
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
