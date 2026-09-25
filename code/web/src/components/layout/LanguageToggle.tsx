"use client";

/**
 * LanguageToggle.tsx — EN / RU pill toggle for the header.
 */

import { useTranslation } from "@/lib/qcd/i18n";
import type { Language } from "@/lib/qcd/types";
import { cn } from "@/lib/utils";

export default function LanguageToggle() {
  const { lang, setLang } = useTranslation();
  const opts: Language[] = ["en", "ru"];
  return (
    <div
      className="inline-flex items-center rounded-full border border-border bg-card p-0.5 text-xs font-medium shadow-sm"
      role="group"
      aria-label="Language toggle"
    >
      {opts.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => setLang(l)}
          aria-pressed={lang === l}
          className={cn(
            "px-3 py-1 rounded-full transition-colors uppercase tracking-wide",
            lang === l
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
