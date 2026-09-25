"use client";

/**
 * HomeView.tsx — Overview dashboard: 9 section cards + quick stats.
 *
 * Clicking a card navigates to the section's live viz view via the SPA nav.
 */

import {
  Activity,
  BarChart3,
  Compass,
  Grid3x3,
  Link2,
  type LucideIcon,
  Target,
  Timer,
  TrendingDown,
  Waves,
  ArrowRight,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PALETTE, SECTIONS, AUTHOR } from "@/lib/qcd/constants";
import { useNav } from "@/lib/qcd/nav";
import { useTranslation } from "@/lib/qcd/i18n";
import { useQCDStore } from "@/lib/qcd/configStore";

const ICONS: Record<string, LucideIcon> = {
  Grid3x3,
  Activity,
  BarChart3,
  TrendingDown,
  Timer,
  Target,
  Compass,
  Link2,
  Waves,
};

const STAT_VALUES: Record<number, string> = {
  1: "28 × 28",
  2: "13 κ_T values",
  3: "Wigner ρ(λ)",
  4: "1/√N → 0",
  5: "5×10⁻⁴¹ s",
  6: "κ_T > 2.62",
  7: "δ < 15%",
  8: "8 steps · 0 new fields",
  9: "χ_eff = δ_C·Λ⁴",
};

export default function HomeView() {
  const { t } = useTranslation();
  const { set } = useNav();
  const { result } = useQCDStore();

  return (
    <div className="space-y-6">
      {/* Hero */}
      <Card className="overflow-hidden border-0 shadow-md">
        <div
          className="p-6 md:p-8 text-white"
          style={{
            background: `linear-gradient(135deg, ${PALETTE.primary} 0%, #2B3E54 50%, ${PALETTE.accent} 130%)`,
          }}
        >
          <Badge variant="secondary" className="mb-3 bg-white/15 text-white border-0">
            {AUTHOR.name} · ORCID {AUTHOR.orcid}
          </Badge>
          <h2 className="text-2xl md:text-3xl font-bold leading-tight">{t("home.heading")}</h2>
          <p className="mt-2 text-sm md:text-base text-slate-200 max-w-3xl">{t("home.intro")}</p>
          {result && (
            <div className="mt-4 inline-flex items-center gap-3 rounded-md bg-white/10 px-3 py-1.5 text-xs">
              <span className="text-slate-200">{t("report.lastRun")}:</span>
              <span className="font-mono">{result.timestamp}</span>
              <span className="text-slate-300">·</span>
              <span className="font-mono">{result.elapsed_s.toFixed(3)}s</span>
              <span className="text-slate-300">·</span>
              <span className="font-mono">[{result.sections_run.join(",")}]</span>
            </div>
          )}
        </div>
      </Card>

      {/* Section cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {SECTIONS.map((s) => {
          const Icon = ICONS[s.icon] ?? Grid3x3;
          return (
            <Card
              key={s.id}
              className="group shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
              onClick={() => set(`section:${s.id}`)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  set(`section:${s.id}`);
                }
              }}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <div
                    className="h-10 w-10 rounded-lg flex items-center justify-center shrink-0"
                    style={{ background: `${PALETTE.bg}`, border: `1px solid ${PALETTE.grid}` }}
                  >
                    <Icon className={`h-5 w-5 ${s.color}`} />
                  </div>
                  <Badge variant="outline" className="font-mono">§{s.id}</Badge>
                </div>
                <CardTitle className="text-base mt-2">
                  {s.id}. {t(`s${s.id}.title`)}
                </CardTitle>
                <CardDescription>{t(`s${s.id}.desc`)}</CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[10px] uppercase tracking-wide text-muted-foreground">
                      {t("home.quickStats")}
                    </div>
                    <div className="text-sm font-mono font-semibold">
                      {t(`s${s.id}.stat`)} · {STAT_VALUES[s.id]}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="opacity-70 group-hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      set(`section:${s.id}`);
                    }}
                  >
                    {t("home.openSection")}
                    <ArrowRight className="ml-1 h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
