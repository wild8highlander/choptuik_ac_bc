"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { LiveChart } from "@/components/live-chart";
import { generate64Structures, SPINOR_PHASES } from "@/lib/compute";
import type { SpinorStructure } from "@/lib/types";
import { Grid3X3, Info, ChevronUp, ChevronDown } from "lucide-react";

type SortKey = "index" | "delta_total" | "eigenvalue" | "symmetry_class";
type SortDir = "asc" | "desc";

export default function StructuresPage() {
  const [selected, setSelected] = useState<SpinorStructure | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("index");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const structures = useMemo(
    () => generate64Structures(SPINOR_PHASES.delta_A, SPINOR_PHASES.delta_B, SPINOR_PHASES.delta_C),
    []
  );

  const sorted = useMemo(() => {
    const arr = [...structures];
    arr.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "index":
          cmp = a.index - b.index;
          break;
        case "delta_total":
          cmp = a.delta_total - b.delta_total;
          break;
        case "eigenvalue":
          cmp = a.eigenvalue - b.eigenvalue;
          break;
        case "symmetry_class":
          cmp = a.symmetry_class.localeCompare(b.symmetry_class);
          break;
      }
      return sortDir === "asc" ? cmp : -cmp;
    });
    return arr;
  }, [structures, sortKey, sortDir]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  // Heatmap data: 8x8 grid
  const heatmapData = useMemo(() => {
    const rows: { row: number; cells: { idx: number; val: number; stable: boolean }[] }[] = [];
    for (let r = 0; r < 8; r++) {
      const cells: { idx: number; val: number; stable: boolean }[] = [];
      for (let c = 0; c < 8; c++) {
        const idx = r * 8 + c;
        const s = structures[idx];
        cells.push({ idx, val: s.delta_total, stable: s.is_stable });
      }
      rows.push({ row: r, cells });
    }
    return rows;
  }, [structures]);

  // Distribution data for chart
  const distributionData = useMemo(() => {
    const bins: Record<string, number> = {};
    structures.forEach((s) => {
      const key = s.symmetry_class;
      bins[key] = (bins[key] || 0) + 1;
    });
    return Object.entries(bins).map(([cls, count]) => ({
      class: cls,
      count,
    }));
  }, [structures]);

  const stableCount = structures.filter((s) => s.is_stable).length;

  const renderSortIcon = (col: SortKey) => {
    if (sortKey !== col) return null;
    return sortDir === "asc" ? (
      <ChevronUp className="h-3 w-3 inline" />
    ) : (
      <ChevronDown className="h-3 w-3 inline" />
    );
  };

  return (
    <div className="space-y-6 animate-slide-up">
      <div>
        <h1 className="text-2xl font-bold text-white">64 Spinor Structures</h1>
        <p className="text-sm text-gray-400 mt-1">
          Explore all spinor structures on the Klein quartic curve
        </p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-teal-400">64</p>
            <p className="text-xs text-gray-400">Total Structures</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-emerald-400">{stableCount}</p>
            <p className="text-xs text-gray-400">Stable</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-amber-400">{64 - stableCount}</p>
            <p className="text-xs text-gray-400">Unstable</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-cyan-400">
              {new Set(structures.map((s) => s.symmetry_class)).size}
            </p>
            <p className="text-xs text-gray-400">Symmetry Classes</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="heatmap">
        <TabsList>
          <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
          <TabsTrigger value="table">Table</TabsTrigger>
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
        </TabsList>

        <TabsContent value="heatmap">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Grid3X3 className="h-5 w-5 text-teal-400" />
                Δ_total Heatmap (8×8)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-6">
                <div className="space-y-0.5">
                  {heatmapData.map((row) => (
                    <div key={row.row} className="flex gap-0.5">
                      {row.cells.map((cell) => {
                        const maxVal = Math.max(...structures.map((s) => s.delta_total));
                        const minVal = Math.min(...structures.map((s) => s.delta_total));
                        const norm = (cell.val - minVal) / (maxVal - minVal + 1e-10);
                        const isHovered = hoveredIdx === cell.idx;
                        return (
                          <div
                            key={cell.idx}
                            className={`w-10 h-10 rounded-sm cursor-pointer transition-all duration-200 border ${
                              isHovered
                                ? "border-white scale-110 z-10"
                                : cell.stable
                                ? "border-navy-600"
                                : "border-navy-700"
                            }`}
                            style={{
                              backgroundColor: `rgb(${Math.round(20 + norm * 20)}, ${Math.round(
                                180 - norm * 100
                              )}, ${Math.round(190 - norm * 80)})`,
                            }}
                            onMouseEnter={() => setHoveredIdx(cell.idx)}
                            onMouseLeave={() => setHoveredIdx(null)}
                            onClick={() => setSelected(structures[cell.idx])}
                            title={`#${cell.idx}: Δ=${cell.val.toFixed(4)}`}
                          />
                        );
                      })}
                    </div>
                  ))}
                </div>

                {/* Hover/Click Detail */}
                <div className="flex-1 min-w-[200px]">
                  {(selected || (hoveredIdx !== null ? structures[hoveredIdx] : null)) && (
                    <Card className="bg-navy-900/50">
                      <CardContent className="p-4 space-y-2">
                        {(() => {
                          const s = selected || (hoveredIdx !== null ? structures[hoveredIdx] : null);
                          if (!s) return null;
                          return (
                            <>
                              <p className="text-sm font-bold text-teal-400">
                                Structure #{s.index}
                              </p>
                              <div className="grid grid-cols-2 gap-1 text-xs">
                                <span className="text-gray-400">Phase A:</span>
                                <span className="font-mono">{s.phase_A.toFixed(4)}</span>
                                <span className="text-gray-400">Phase B:</span>
                                <span className="font-mono">{s.phase_B.toFixed(4)}</span>
                                <span className="text-gray-400">Phase C:</span>
                                <span className="font-mono">{s.phase_C.toFixed(4)}</span>
                                <span className="text-gray-400">Δ_total:</span>
                                <span className="font-mono text-teal-400">
                                  {s.delta_total.toFixed(4)}
                                </span>
                                <span className="text-gray-400">Eigenvalue:</span>
                                <span className="font-mono">{s.eigenvalue.toFixed(4)}</span>
                                <span className="text-gray-400">Symmetry:</span>
                                <span className="font-mono">{s.symmetry_class}</span>
                                <span className="text-gray-400">Stable:</span>
                                <Badge variant={s.is_stable ? "success" : "destructive"}>
                                  {s.is_stable ? "Yes" : "No"}
                                </Badge>
                              </div>
                            </>
                          );
                        })()}
                      </CardContent>
                    </Card>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="table">
          <Card>
            <CardHeader>
              <CardTitle>Sortable Structure Table</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="max-h-[500px] overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead
                        className="cursor-pointer"
                        onClick={() => handleSort("index")}
                      >
                        # {renderSortIcon("index")}
                      </TableHead>
                      <TableHead>δ_A</TableHead>
                      <TableHead>δ_B</TableHead>
                      <TableHead>δ_C</TableHead>
                      <TableHead
                        className="cursor-pointer"
                        onClick={() => handleSort("delta_total")}
                      >
                        Δ_total {renderSortIcon("delta_total")}
                      </TableHead>
                      <TableHead
                        className="cursor-pointer"
                        onClick={() => handleSort("eigenvalue")}
                      >
                        Eigenvalue {renderSortIcon("eigenvalue")}
                      </TableHead>
                      <TableHead
                        className="cursor-pointer"
                        onClick={() => handleSort("symmetry_class")}
                      >
                        Sym {renderSortIcon("symmetry_class")}
                      </TableHead>
                      <TableHead>Stable</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sorted.map((s) => (
                      <TableRow
                        key={s.index}
                        className="cursor-pointer"
                        onClick={() => setSelected(s)}
                      >
                        <TableCell className="font-mono text-xs">{s.index}</TableCell>
                        <TableCell className="font-mono text-xs">
                          {s.phase_A.toFixed(3)}
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {s.phase_B.toFixed(3)}
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {s.phase_C.toFixed(3)}
                        </TableCell>
                        <TableCell className="font-mono text-xs text-teal-400">
                          {s.delta_total.toFixed(4)}
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {s.eigenvalue.toFixed(4)}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-[10px]">
                            {s.symmetry_class}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={s.is_stable ? "success" : "destructive"} className="text-[10px]">
                            {s.is_stable ? "✓" : "✗"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="distribution">
          <Card>
            <CardHeader>
              <CardTitle>Symmetry Class Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <LiveChart
                data={distributionData}
                xKey="class"
                lines={[{ key: "count", color: "#14b8a6", name: "Structures" }]}
                type="bar"
                height={300}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Selected Structure Detail */}
      {selected && (
        <Card className="border-teal-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5 text-teal-400" />
              Structure #{selected.index} — Detailed Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-400">Phase A</p>
                <p className="font-mono text-lg text-teal-400">
                  {selected.phase_A.toFixed(6)}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Phase B</p>
                <p className="font-mono text-lg text-teal-400">
                  {selected.phase_B.toFixed(6)}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Phase C</p>
                <p className="font-mono text-lg text-teal-400">
                  {selected.phase_C.toFixed(6)}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Δ_total</p>
                <p className="font-mono text-lg text-science-violet">
                  {selected.delta_total.toFixed(6)}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Eigenvalue</p>
                <p className="font-mono text-lg text-white">
                  {selected.eigenvalue.toFixed(6)}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Symmetry</p>
                <p className="font-mono text-lg text-white">
                  {selected.symmetry_class}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Stability</p>
                <Badge variant={selected.is_stable ? "success" : "destructive"}>
                  {selected.is_stable ? "Stable" : "Unstable"}
                </Badge>
              </div>
              <div>
                <p className="text-gray-400">Index</p>
                <p className="font-mono text-lg text-gray-300">{selected.index}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
