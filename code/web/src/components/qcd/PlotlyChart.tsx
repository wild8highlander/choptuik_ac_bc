"use client";

/**
 * PlotlyChart.tsx — Dynamic-imported Plotly wrapper.
 *
 * Plotly.js touches `window` at import time, so we lazy-load it inside a
 * client effect and surface a loading skeleton until the figure is drawn.
 * The wrapper supports the small subset of figure fields we actually use
 * (data traces, layout, config) — no need for the full plotly.js type tree.
 */

import { useEffect, useRef, useState } from "react";
import { PALETTE } from "@/lib/qcd/constants";
import { useTranslation } from "@/lib/qcd/i18n";

// Plotly figure types — intentionally minimal.
export interface PlotlyTrace {
  type?: string;
  x?: number[] | string[];
  y?: number[] | string[];
  z?: number[] | number[][];
  i?: number[];
  j?: number[];
  k?: number[];
  a?: number[];
  b?: number[];
  c?: number[];
  u?: number[];
  v?: number[];
  w?: number[];
  name?: string;
  mode?: string;
  marker?: Record<string, unknown>;
  line?: Record<string, unknown>;
  surface?: Record<string, unknown>;
  text?: string[] | string;
  hovertemplate?: string;
  showlegend?: boolean;
  opacity?: number;
  color?: string | string[];
  colorscale?: string | Array<[number, string]>;
  showscale?: boolean;
  width?: number;
  sizeref?: number;
  sizemode?: string;
  sizemin?: number;
  [k: string]: unknown;
}

export interface PlotlyFigure {
  data: PlotlyTrace[];
  layout?: Record<string, unknown>;
  config?: Record<string, unknown>;
}

interface Props {
  figure: PlotlyFigure;
  className?: string;
  /** Plot height in pixels. */
  height?: number;
}

export default function PlotlyChart({ figure, className, height = 460 }: Props) {
  const elRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const { t } = useTranslation();

  useEffect(() => {
    let cancelled = false;
    let plotly: any;

    (async () => {
      try {
        // plotly.js-dist-min is a UMD bundle that mutates `window.Plotly`.
        const mod: any = await import("plotly.js-dist-min");
        plotly = mod.default ?? mod;
        if (cancelled || !elRef.current) return;

        const layout = Object.assign(
          {
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: { family: "Inter, system-ui, sans-serif", size: 12, color: PALETTE.ink },
            margin: { l: 60, r: 30, t: 50, b: 50 },
            scene: {
              xaxis: { title: { text: "x" }, gridcolor: PALETTE.grid, backgroundcolor: "rgba(248,250,252,0.6)" },
              yaxis: { title: { text: "y" }, gridcolor: PALETTE.grid, backgroundcolor: "rgba(248,250,252,0.6)" },
              zaxis: { title: { text: "z" }, gridcolor: PALETTE.grid, backgroundcolor: "rgba(248,250,252,0.6)" },
              camera: { eye: { x: 1.4, y: 1.4, z: 0.9 } },
            },
            legend: { orientation: "h", y: -0.2 },
            hoverlabel: { bgcolor: PALETTE.primary, font: { color: "#fff" } },
          },
          figure.layout ?? {},
        );

        const config = Object.assign(
          {
            responsive: true,
            displaylogo: false,
            displayModeBar: true,
            modeBarButtonsToRemove: ["lasso2d", "select2d"],
            toImageButtonOptions: {
              format: "png",
              filename: "choptuik_qcd_bridge",
              height: 720,
              width: 1080,
              scale: 2,
            },
          },
          figure.config ?? {},
        );

        plotly.react(elRef.current, figure.data, layout, config);
        if (!cancelled) setStatus("ready");
      } catch (err) {
        console.error("Plotly render failed", err);
        if (!cancelled) setStatus("error");
      }
    })();

    return () => {
      cancelled = true;
      if (plotly && elRef.current) {
        try {
          plotly.purge(elRef.current);
        } catch {
          /* ignore */
        }
      }
    };
  }, [figure]);

  return (
    <div className={className} style={{ position: "relative" }}>
      <div ref={elRef} style={{ width: "100%", height }} aria-label="Plotly chart" />
      {status === "loading" && (
        <div
          className="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground bg-card/60 backdrop-blur-sm rounded-md"
          aria-live="polite"
        >
          <span className="inline-flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-accent animate-pulse" />
            {t("plot.loading")}
          </span>
        </div>
      )}
      {status === "error" && (
        <div className="absolute inset-0 flex items-center justify-center text-sm text-destructive">
          Plotly failed to render. Check the browser console.
        </div>
      )}
    </div>
  );
}
