"use client";

/**
 * AppShell.tsx — Sidebar + header + sticky footer layout for the SPA.
 *
 * The shell wires the sidebar nav (Home + 9 sections + About) to the
 * `useNav` hook so a single click updates the visible section without
 * changing the URL (per system constraint: only `/` is exposed).
 */

import Link from "next/link";
import {
  Activity,
  BarChart3,
  BookOpen,
  Compass,
  Grid3x3,
  Home,
  LayoutDashboard,
  Link2,
  Target,
  Timer,
  TrendingDown,
  Waves,
  Github,
  ExternalLink,
} from "lucide-react";
import { useNav } from "@/lib/qcd/nav";
import { SECTIONS, AUTHOR, PALETTE } from "@/lib/qcd/constants";
import { useTranslation } from "@/lib/qcd/i18n";
import LanguageToggle from "./LanguageToggle";
import { cn } from "@/lib/utils";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
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

type NavKey = "home" | "dashboard" | `section:${number}` | "about";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { current, set } = useNav();
  const { t } = useTranslation();

  const navItems: { key: NavKey; label: string; icon?: React.ComponentType<{ className?: string }>; sectionId?: number }[] = [
    { key: "home",  label: t("nav.home"),  icon: Home },
    { key: "dashboard", label: t("nav.dashboard"), icon: LayoutDashboard },
    ...SECTIONS.map((s) => ({
      key: `section:${s.id}` as NavKey,
      label: `${s.id}. ${t(`s${s.id}.title`)}`,
      icon: ICONS[s.icon] ?? Grid3x3,
      sectionId: s.id,
    })),
    { key: "about", label: t("nav.about"), icon: BookOpen },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-background" style={{ background: PALETTE.bg }}>
      {/* Header */}
      <header
        className="sticky top-0 z-30 flex items-center justify-between gap-4 px-4 md:px-6 py-3 border-b backdrop-blur"
        style={{
          background: `linear-gradient(180deg, ${PALETTE.primary} 0%, #2B3E54 100%)`,
          borderColor: "rgba(255,255,255,0.08)",
          color: "#F8FAFC",
        }}
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="h-9 w-9 rounded-lg flex items-center justify-center shadow-inner"
               style={{ background: PALETTE.accent }}>
            <Waves className="h-5 w-5 text-white" />
          </div>
          <div className="min-w-0">
            <h1 className="text-base md:text-lg font-semibold truncate text-white">{t("app.title")}</h1>
            <p className="text-[11px] md:text-xs text-slate-300 truncate">{t("app.subtitle")}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <a
            href={AUTHOR.github}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1 text-xs text-slate-200 hover:text-white"
            aria-label="GitHub repository"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
          <LanguageToggle />
        </div>
      </header>

      <div className="flex flex-1 w-full max-w-[1500px] mx-auto">
        {/* Sidebar */}
        <aside
          className="hidden md:flex flex-col w-64 shrink-0 border-r bg-card"
          style={{ borderColor: PALETTE.grid }}
          aria-label="Sections navigation"
        >
          <nav className="flex-1 overflow-y-auto p-3 max-h-[calc(100vh-3.5rem)]">
            <ul className="space-y-1">
              {navItems.map((it) => {
                const Icon = it.icon ?? Home;
                const active = current === it.key;
                return (
                  <li key={it.key}>
                    <button
                      type="button"
                      onClick={() => set(it.key)}
                      aria-current={active ? "page" : undefined}
                      className={cn(
                        "w-full flex items-start gap-3 rounded-md px-3 py-2 text-left text-sm transition-colors",
                        active
                          ? "bg-primary text-primary-foreground shadow-sm"
                          : "text-foreground hover:bg-muted",
                      )}
                    >
                      <Icon className="h-4 w-4 mt-0.5 shrink-0" />
                      <span className="leading-snug">{it.label}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>
          <div
            className="p-3 text-[11px] text-muted-foreground border-t"
            style={{ borderColor: PALETTE.grid }}
          >
            <div className="font-medium text-foreground">{AUTHOR.name}</div>
            <div className="mt-1">
              ORCID:{" "}
              <a
                href={AUTHOR.orcidUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent hover:underline inline-flex items-center gap-0.5"
              >
                {AUTHOR.orcid}
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        </aside>

        {/* Mobile top-level nav (chips) */}
        <div className="md:hidden -mt-px flex overflow-x-auto gap-2 px-3 py-2 border-b bg-card"
             style={{ borderColor: PALETTE.grid }}>
          {navItems.map((it) => {
            const active = current === it.key;
            return (
              <button
                key={it.key}
                type="button"
                onClick={() => set(it.key)}
                className={cn(
                  "whitespace-nowrap rounded-full px-3 py-1 text-xs",
                  active ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
                )}
              >
                {it.label}
              </button>
            );
          })}
        </div>

        {/* Main */}
        <main className="flex-1 min-w-0 p-4 md:p-6 lg:p-8" id="main-content">
          {children}
        </main>
      </div>

      {/* Sticky footer */}
      <footer
        className="mt-auto border-t"
        style={{ background: PALETTE.primary, borderColor: "rgba(255,255,255,0.08)", color: "#CBD5E1" }}
      >
        <div className="max-w-[1500px] mx-auto px-4 md:px-6 py-3 flex flex-col md:flex-row gap-2 md:items-center md:justify-between text-xs">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <span>
              <span className="text-slate-400">{t("footer.author")}:</span>{" "}
              <span className="text-white font-medium">{AUTHOR.name}</span>
            </span>
            <span>
              <span className="text-slate-400">{t("footer.orcid")}:</span>{" "}
              <Link href={AUTHOR.orcidUrl} className="hover:text-white hover:underline" target="_blank">
                {AUTHOR.orcid}
              </Link>
            </span>
            <a href={AUTHOR.github} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-1 hover:text-white">
              <Github className="h-3 w-3" /> {t("footer.repo")}
            </a>
            <span>
              <span className="text-slate-400">{t("footer.license")}:</span> {AUTHOR.license}
            </span>
          </div>
          <div className="text-slate-400">{t("footer.poweredBy")}</div>
        </div>
      </footer>
    </div>
  );
}
