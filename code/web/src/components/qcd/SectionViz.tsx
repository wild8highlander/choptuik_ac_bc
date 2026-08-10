"use client";

/**
 * SectionViz.tsx — Render a single section's Plotly figure + stat tiles
 * + optional data table. Subscribes to the live config store so any
 * parameter change re-renders the figure client-side.
 */

import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import { ExternalLink, Image as ImageIcon } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useQCDStore } from "@/lib/qcd/configStore";
import { useTranslation } from "@/lib/qcd/i18n";
import { buildSectionFigure, type StatTile } from "@/lib/qcd/figures";
import { cn } from "@/lib/utils";

// Plotly needs the browser — load it lazily.
const PlotlyChart = dynamic(() => import("@/components/qcd/PlotlyChart"), {
  ssr: false,
  loading: () => (
    <div className="h-[460px] flex items-center justify-center text-sm text-muted-foreground">
      Loading Plotly…
    </div>
  ),
});

const TONE_CLASS: Record<NonNullable<StatTile["tone"]>, string> = {
  default: "bg-muted text-foreground",
  good: "bg-emerald-50 text-emerald-700 border-emerald-200",
  warn: "bg-amber-50 text-amber-800 border-amber-200",
  bad: "bg-rose-50 text-rose-700 border-rose-200",
};

function StatCard({ tile }: { tile: StatTile }) {
  const { t } = useTranslation();
  const tone = tile.tone ?? "default";
  return (
    <div
      className={cn(
        "rounded-lg border p-3 flex flex-col gap-1",
        TONE_CLASS[tone],
      )}
    >
      <span className="text-[10px] uppercase tracking-wide opacity-80">
        {t(tile.label)}
      </span>
      <span className="text-sm font-semibold font-mono break-all leading-tight">{tile.value}</span>
      {tile.hint && <span className="text-[10px] opacity-70">{tile.hint}</span>}
    </div>
  );
}

export default function SectionViz({ sectionId }: { sectionId: number }) {
  const config = useQCDStore((s) => s.config);
  const result = useQCDStore((s) => s.result);
  const { t } = useTranslation();
  const [showStatic, setShowStatic] = useState<"3d" | "4d" | null>(null);

  const { figure, stats, table } = useMemo(
    () => buildSectionFigure(sectionId, config),
    [sectionId, config],
  );

  // If we have a Python result for this section, surface a badge.
  const pythonBadge = result && result.sections_run.includes(sectionId);

  return (
    <div className="space-y-4">
      <Card className="shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                {sectionId}. {t(`s${sectionId}.title`)}
                {pythonBadge ? (
                  <Badge variant="default" className="text-[10px]">
                    Python: {result!.elapsed_s.toFixed(2)}s
                  </Badge>
                ) : null}
              </CardTitle>
              <CardDescription>{t(`s${sectionId}.desc`)}</CardDescription>
            </div>
            <Badge variant="outline" className="font-mono">
              {t(`s${sectionId}.short`)}
            </Badge>
          </div>
          <div className="flex flex-wrap gap-2 pt-2">
            <Button
              size="sm"
              variant={showStatic === null ? "default" : "outline"}
              onClick={() => setShowStatic(null)}
              className="h-7 text-xs"
            >
              <ImageIcon className="h-3 w-3 mr-1" />
              Live 3D
            </Button>
            <Button
              size="sm"
              variant={showStatic === "3d" ? "default" : "outline"}
              onClick={() => setShowStatic("3d")}
              className="h-7 text-xs"
            >
              Static 3D PNG
            </Button>
            <Button
              size="sm"
              variant={showStatic === "4d" ? "default" : "outline"}
              onClick={() => setShowStatic("4d")}
              className="h-7 text-xs"
            >
              Static 4D PNG
            </Button>
            <a
              href={`/api/figures/${sectionId}?variant=4d`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-accent hover:underline ml-auto"
            >
              <ExternalLink className="h-3 w-3" />
              {t("common.viewFigure")}
            </a>
          </div>
        </CardHeader>
        <CardContent>
          {showStatic === null ? (
            <PlotlyChart figure={figure} height={460} />
          ) : (
            <div className="rounded-md border bg-card overflow-hidden">
              <img
                src={`/api/figures/${sectionId}?variant=${showStatic}`}
                alt={`Section ${sectionId} ${showStatic} figure`}
                className="w-full h-[460px] object-contain bg-white"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {stats.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {stats.map((s, i) => (
            <StatCard key={i} tile={s} />
          ))}
        </div>
      )}

      {table && (
        <Card className="shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Data table</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="max-h-72 rounded-md border">
              <Table>
                <TableHeader sticky>
                  <TableRow>
                    {table.columns.map((c) => (
                      <TableHead key={c} className="text-xs">{t(c)}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {table.rows.map((row, i) => (
                    <TableRow key={i}>
                      {row.map((cell, j) => (
                        <TableCell key={j} className="text-xs font-mono py-1.5">{cell}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
