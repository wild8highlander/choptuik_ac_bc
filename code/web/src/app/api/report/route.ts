/**
 * /api/report/route.ts — Generate a report file via the Python report engine.
 *
 * POST body: the live QCDConfig + a single `format` field. The route spawns
 * `python3 web_runner.py report --format <fmt> --output-dir <web/output>`,
 * parses the JSON manifest, and returns:
 *   { path: "<abs path on disk>", download_url: "/api/report/download?file=..." }
 *
 * The frontend then triggers an anchor download against `download_url`.
 */

import { NextResponse } from "next/server";
import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { tmpdir } from "node:os";
import { mkdir, writeFile, readFile, unlink, stat } from "node:fs/promises";
import { join, basename, extname } from "node:path";
import type { QCDConfig, ReportFormat } from "@/lib/qcd/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const PYTHON_BIN = process.env.QCD_PYTHON ?? "python3";
const WEB_RUNNER = "/home/z/my-project/choptuik_ac_bc/code/python/web_runner.py";
const WEB_OUTPUT = "/home/z/my-project/choptuik_ac_bc/code/web/output";

const VALID_FORMATS: ReportFormat[] = ["txt", "csv", "md", "pdf", "html", "docx", "json"];

export async function POST(req: Request) {
  let cfg: Partial<QCDConfig> & { format?: ReportFormat };
  try {
    cfg = (await req.json()) as Partial<QCDConfig> & { format?: ReportFormat };
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const fmt: ReportFormat = (cfg.format ?? "json") as ReportFormat;
  if (!VALID_FORMATS.includes(fmt)) {
    return NextResponse.json({ error: `Invalid format: ${fmt}` }, { status: 400 });
  }

  const payload: QCDConfig = {
    mode: cfg.mode ?? "custom",
    sections: cfg.sections ?? [1, 2, 3, 4, 5, 6, 7, 8, 9],
    kappa_values: cfg.kappa_values ?? [
      0.0, 0.3, 0.7, 1.0, 1.5, 2.0, 2.62, 3.0, 4.0, 5.0, 8.45, 12.0, 20.0,
    ],
    N_values: cfg.N_values ?? [10, 28, 50, 100, 200, 500, 1000, 2000, 5000],
    kappa_T_custom: cfg.kappa_T_custom ?? 8.45,
    N_custom: cfg.N_custom ?? 28,
    n_flavors: cfg.n_flavors ?? 6,
    seed: cfg.seed ?? 42,
    language: cfg.language ?? "en",
    report_formats: [fmt],
  };

  await mkdir(WEB_OUTPUT, { recursive: true });
  const tmp = join(tmpdir(), `qcd-report-${randomUUID()}.json`);
  await writeFile(tmp, JSON.stringify(payload), "utf8");

  try {
    const { stdout, stderr, code } = await runPython(
      WEB_RUNNER,
      "report",
      tmp,
      ["--output-dir", WEB_OUTPUT, "--format", fmt],
    );
    if (code !== 0) {
      return NextResponse.json(
        { error: `Python runner exited ${code}`, stderr: stderr.slice(-2000) },
        { status: 500 },
      );
    }
    const manifestLine = stdout.split("\n").find((l) => l.startsWith("{"));
    if (!manifestLine) {
      return NextResponse.json({ error: "No manifest from runner", stdout }, { status: 500 });
    }
    const manifest = JSON.parse(manifestLine) as {
      ok: boolean;
      output_dir: string;
      paths: Record<string, string>;
      formats_requested: string[];
      timestamp: string;
      elapsed_s: number;
    };
    const path = manifest.paths[fmt];
    if (!path || path.startsWith("ERROR")) {
      return NextResponse.json(
        { error: `Failed to generate ${fmt}: ${path}`, manifest },
        { status: 500 },
      );
    }
    // Verify the file exists.
    const info = await stat(path);
    const filename = basename(path);
    const downloadUrl = `/api/report?file=${encodeURIComponent(filename)}`;
    return NextResponse.json({
      path,
      download_url: downloadUrl,
      size_bytes: info.size,
      timestamp: manifest.timestamp,
      elapsed_s: manifest.elapsed_s,
      format: fmt,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  } finally {
    await unlink(tmp).catch(() => {});
  }
}

/** GET — stream a previously-generated report file from /web/output/. */
export async function GET(req: Request) {
  const url = new URL(req.url);
  const file = url.searchParams.get("file");
  if (!file) {
    return NextResponse.json({ error: "Missing ?file=" }, { status: 400 });
  }
  // Reject path traversal.
  if (file.includes("..") || file.includes("/")) {
    return NextResponse.json({ error: "Invalid filename" }, { status: 400 });
  }
  const full = join(WEB_OUTPUT, file);
  try {
    const buf = await readFile(full);
    const ext = extname(file).toLowerCase().slice(1);
    const contentType =
      ext === "pdf" ? "application/pdf" :
      ext === "html" ? "text/html; charset=utf-8" :
      ext === "docx" ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document" :
      ext === "json" ? "application/json; charset=utf-8" :
      ext === "csv" ? "text/csv; charset=utf-8" :
      "text/plain; charset=utf-8";
    return new NextResponse(buf, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `attachment; filename="${file}"`,
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return NextResponse.json({ error: `File not found: ${file}` }, { status: 404 });
  }
}

function runPython(
  scriptPath: string,
  command: string,
  payloadPath: string,
  extraArgs: string[] = [],
): Promise<{ stdout: string; stderr: string; code: number | null }> {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON_BIN, [scriptPath, command, ...extraArgs], {
      cwd: "/home/z/my-project/choptuik_ac_bc/code/python",
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", reject);
    child.on("close", (code) => resolve({ stdout, stderr, code }));

    (async () => {
      const data = await readFile(payloadPath);
      child.stdin.write(data);
      child.stdin.end();
    })().catch((e) => {
      try {
        child.kill();
      } catch {
        /* ignore */
      }
      reject(e);
    });
  });
}
