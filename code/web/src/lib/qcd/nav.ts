"use client";

/**
 * nav.ts — Tiny SPA navigation store.
 *
 * We avoid Next.js routing so that only `/` is exposed (per the system
 * constraint) but still let users navigate between Home, the 9 sections,
 * and About via in-app state.
 */

import { useSyncExternalStore } from "react";

export type NavKey = "home" | "dashboard" | `section:${number}` | "about";

let current: NavKey = "home";
const listeners = new Set<() => void>();

function emit() {
  for (const l of listeners) l();
}

export function setNav(key: NavKey) {
  if (key === current) return;
  current = key;
  if (typeof window !== "undefined") {
    window.history.replaceState(null, "", `?view=${key}`);
    window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
  }
  emit();
}

export function getNav(): NavKey {
  return current;
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

/** Initialize from URL `?view=` query (called on first client render). */
export function initNavFromURL() {
  if (typeof window === "undefined") return;
  const params = new URLSearchParams(window.location.search);
  const v = params.get("view");
  if (v === "home" || v === "dashboard" || v === "about" || /^section:\d+$/.test(v)) {
    current = v as NavKey;
    emit();
  }
}

/** React hook returning the current nav key + setter. */
export function useNav(): { current: NavKey; set: (k: NavKey) => void } {
  const cur = useSyncExternalStore(subscribe, getNav, getNav);
  return { current: cur, set: setNav };
}
