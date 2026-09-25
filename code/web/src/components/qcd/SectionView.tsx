"use client";

/**
 * SectionView.tsx — Composes ParamPanel + SectionViz + ReportPanel for a
 * single section view, with a small section switcher at the top.
 */

import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SECTIONS } from "@/lib/qcd/constants";
import { useNav } from "@/lib/qcd/nav";
import { useTranslation } from "@/lib/qcd/i18n";
import ParamPanel from "./ParamPanel";
import SectionViz from "./SectionViz";
import ReportPanel from "./ReportPanel";

export default function SectionView({ sectionId }: { sectionId: number }) {
  const { t } = useTranslation();
  const { set } = useNav();

  const idx = SECTIONS.findIndex((s) => s.id === sectionId);
  const prev = SECTIONS[idx - 1];
  const next = SECTIONS[idx + 1];

  return (
    <div className="space-y-6">
      {/* Section pager */}
      <div className="flex items-center justify-between gap-2">
        <Button
          variant="ghost"
          size="sm"
          disabled={!prev}
          onClick={() => prev && set(`section:${prev.id}`)}
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          {prev ? `§${prev.id} ${t(`s${prev.id}.short`)}` : "—"}
        </Button>
        <Badge variant="outline" className="font-mono">
          Section {sectionId} / {SECTIONS[SECTIONS.length - 1].id}
        </Badge>
        <Button
          variant="ghost"
          size="sm"
          disabled={!next}
          onClick={() => next && set(`section:${next.id}`)}
        >
          {next ? `§${next.id} ${t(`s${next.id}.short`)}` : "—"}
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <SectionViz sectionId={sectionId} />
        </div>
        <div className="space-y-4">
          <ParamPanel />
          <ReportPanel />
        </div>
      </div>
    </div>
  );
}
