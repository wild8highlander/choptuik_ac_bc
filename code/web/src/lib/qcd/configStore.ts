"use client";

/**
 * configStore.ts — Zustand store holding the live QCDConfig + the last
 * Python-backed QCDResult (if any). All section components subscribe to this
 * store so a parameter change instantly recomputes the local preview.
 */

import { create } from "zustand";
import { DEFAULT_CONFIG, type QCDConfig, type QCDResult } from "./types";

interface QCDStore {
  config: QCDConfig;
  result: QCDResult | null;
  runStatus: "idle" | "running" | "ok" | "error";
  runError: string | null;
  setConfig: (patch: Partial<QCDConfig>) => void;
  toggleSection: (id: number) => void;
  resetConfig: () => void;
  setResult: (r: QCDResult | null) => void;
  setRunStatus: (s: QCDStore["runStatus"], err?: string | null) => void;
}

export const useQCDStore = create<QCDStore>((set) => ({
  config: { ...DEFAULT_CONFIG },
  result: null,
  runStatus: "idle",
  runError: null,
  setConfig: (patch) =>
    set((s) => ({ config: { ...s.config, ...patch } })),
  toggleSection: (id) =>
    set((s) => {
      const has = s.config.sections.includes(id);
      const sections = has
        ? s.config.sections.filter((x) => x !== id)
        : [...s.config.sections, id].sort((a, b) => a - b);
      return { config: { ...s.config, sections } };
    }),
  resetConfig: () => set({ config: { ...DEFAULT_CONFIG } }),
  setResult: (r) => set({ result: r }),
  setRunStatus: (status, err = null) => set({ runStatus: status, runError: err }),
}));
