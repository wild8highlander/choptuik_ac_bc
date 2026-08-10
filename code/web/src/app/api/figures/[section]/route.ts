/**
 * /api/figures/[section]/route.ts — Serve the canonical Python-generated
 * 3D/4D figure PNG for a given section.
 *
 * Path params:
 *   section: 1..9 (matches the Python engine section id)
 *
 * Query params:
 *   variant: "3d" | "4d"   (default "3d")
 *   format:  "png" | "path" (default "png" — returns image bytes; "path"
 *            returns JSON with the absolute path on disk)
 */

import { NextResponse } from "next/server";
import { readFile, stat } from "node:fs/promises";
import { join } from "node:path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const FIG_DIR = "/home/z/my-project/choptuik_ac_bc/qcd_bridge/figures";

// Maps section id → figure file prefix (matches generate_figures_3d_4d.py).
const FIG_PREFIX: Record<number, string> = {
  1: "fig_s1_ochi_eigvals",     // section 1 has matrix_4d + eigvals_3d; we expose eigvals for 3d
  2: "fig_s2_rmt_sweep",
  3: "fig_s3_staircase",
  4: "fig_s4_N_scaling",
  5: "fig_s5_tau_relax",
  6: "fig_s6_kappa_T",
  7: "fig_s7_cabibbo",
  8: "fig_s8_cp_chain",
  9: "fig_s9_jet_wake",
};

// Special case: section 1 4d uses a different file name.
const SECTION1_4D = "fig_s1_ochi_matrix_4d.png";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ section: string }> },
) {
  const { section: sectionStr } = await params;
  const section = Number(sectionStr);
  if (!Number.isInteger(section) || section < 1 || section > 9) {
    return NextResponse.json({ error: `Invalid section: ${sectionStr}` }, { status: 400 });
  }
  const url = new URL(_req.url);
  const variant = url.searchParams.get("variant") === "4d" ? "4d" : "3d";
  const format = url.searchParams.get("format") === "path" ? "path" : "png";

  // Resolve the file path.
  let filename: string;
  if (section === 1 && variant === "4d") {
    filename = SECTION1_4D;
  } else {
    filename = `${FIG_PREFIX[section]}_${variant}.png`;
  }
  const fullPath = join(FIG_DIR, filename);

  try {
    const info = await stat(fullPath);
    if (format === "path") {
      return NextResponse.json({
        section,
        variant,
        path: fullPath,
        size_bytes: info.size,
        url: `/api/figures/${section}?variant=${variant}`,
      });
    }
    const buf = await readFile(fullPath);
    return new NextResponse(new Uint8Array(buf), {
      status: 200,
      headers: {
        "Content-Type": "image/png",
        "Cache-Control": "public, max-age=3600, immutable",
        "Content-Length": String(buf.length),
      },
    });
  } catch {
    return NextResponse.json(
      { error: `Figure not found: ${filename}`, section, variant },
      { status: 404 },
    );
  }
}
