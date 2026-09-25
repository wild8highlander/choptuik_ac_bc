/**
 * /api/run/route.ts — Dispatch the Python engine and return the full result.
 *
 * The route spawns `python3 web_runner.py run` with the request JSON on stdin
 * (max 60s budget). On success it returns the canonical QCDResult JSON.
 */

import { NextResponse } from "next/server";
import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { tmpdir } from "node:os";
import { mkdir, writeFile, readFile, unlink } from "node:fs/promises";
import { join } from "node:path";
import type { QCDConfig, QCDResult } from "@/lib/qcd/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const PYTHON_BIN = process.env.QCD_PYTHON ?? "python3";
const WEB_RUNNER = "/home/z/my-project/choptuik_ac_bc/code/python/web_runner.py";

export async function POST(req: Request) {
  let cfg: Partial<QCDConfig>;
  try {
    cfg = (await req.json()) as Partial<QCDConfig>;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  // Defensive defaults.
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
    report_formats: cfg.report_formats ?? ["txt", "csv", "md", "pdf", "html", "docx", "json"],
  };

  // Use a temp file rather than piping stdin — avoids Node/Python pipe races
  // for larger N values where the engine takes a few seconds.
  const tmp = join(tmpdir(), `qcd-run-${randomUUID()}.json`);
  await mkdir(tmpdir(), { recursive: true });
  await writeFile(tmp, JSON.stringify(payload), "utf8");

  try {
    const { stdout, stderr, code } = await runPython(WEB_RUNNER, "run", tmp);
    if (code !== 0) {
      return NextResponse.json(
        { error: `Python runner exited with code ${code}`, stderr: stderr.slice(-2000) },
        { status: 500 },
      );
    }
    const result = JSON.parse(stdout.split("\n").find((l) => l.startsWith("{")) ?? "{}") as QCDResult;
    if ((result as unknown as { error?: string }).error) {
      return NextResponse.json(
        { error: (result as unknown as { error: string }).error },
        { status: 500 },
      );
    }
    return NextResponse.json(result);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  } finally {
    await unlink(tmp).catch(() => {});
  }
}

function runPython(scriptPath: string, command: string, payloadPath: string): Promise<{
  stdout: string;
  stderr: string;
  code: number | null;
}> {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON_BIN, [scriptPath, command], {
      cwd: "/home/z/my-project/choptuik_ac_bc/code/python",
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", reject);
    child.on("close", (code) => resolve({ stdout, stderr, code }));

    // Stream the payload file into stdin (works whether or not a TTY is attached).
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
