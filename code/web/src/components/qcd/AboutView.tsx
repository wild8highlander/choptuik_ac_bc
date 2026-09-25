"use client";

/**
 * AboutView.tsx — Author bio, ORCID link, GitHub repo, monograph reference.
 */

import {
  BookOpen,
  ExternalLink,
  Github,
  IdCard,
  Layers,
  Mail,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AUTHOR, PALETTE } from "@/lib/qcd/constants";
import { useTranslation } from "@/lib/qcd/i18n";

export default function AboutView() {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <Card className="shadow-sm overflow-hidden">
        <div
          className="px-6 py-5 text-white"
          style={{
            background: `linear-gradient(135deg, ${PALETTE.primary} 0%, ${PALETTE.accent} 140%)`,
          }}
        >
          <Badge variant="secondary" className="mb-2 bg-white/15 text-white border-0">
            {t("about.title")}
          </Badge>
          <h2 className="text-2xl font-bold">{AUTHOR.name}</h2>
          <p className="text-sm text-slate-200 mt-1">
            {t("app.title")} · {t("app.subtitle")}
          </p>
        </div>
        <CardContent className="pt-6">
          <p className="text-sm leading-relaxed text-foreground">{t("about.bio")}</p>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="shadow-none border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <IdCard className="h-4 w-4" /> {t("about.author")}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <div>
                  <span className="text-muted-foreground">{t("about.author")}: </span>
                  <span className="font-medium">{AUTHOR.name}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">{t("about.orcid")}: </span>
                  <a
                    href={AUTHOR.orcidUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-accent hover:underline"
                  >
                    {AUTHOR.orcid}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-none border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Github className="h-4 w-4" /> {t("about.repo")}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <a
                  href={AUTHOR.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-accent hover:underline break-all"
                >
                  {AUTHOR.github}
                  <ExternalLink className="h-3 w-3 shrink-0" />
                </a>
                <div>
                  <span className="text-muted-foreground">{t("about.license")}: </span>
                  <span className="font-medium">{AUTHOR.license}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-none border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <BookOpen className="h-4 w-4" /> {t("about.monograph")}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <div className="flex items-center justify-between">
                  <span>EN: <span className="font-mono">{AUTHOR.monographEn}</span></span>
                </div>
                <div className="flex items-center justify-between">
                  <span>RU: <span className="font-mono">{AUTHOR.monographRu}</span></span>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-none border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Layers className="h-4 w-4" /> {t("about.stack")}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm">
                {t("about.stackText")}
              </CardContent>
            </Card>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            <Button asChild size="sm">
              <a href={AUTHOR.orcidUrl} target="_blank" rel="noopener noreferrer">
                <IdCard className="h-4 w-4 mr-2" /> ORCID
              </a>
            </Button>
            <Button asChild size="sm" variant="outline">
              <a href={AUTHOR.github} target="_blank" rel="noopener noreferrer">
                <Github className="h-4 w-4 mr-2" /> GitHub
              </a>
            </Button>
            <Button asChild size="sm" variant="outline">
              <a href={`mailto:researcher@example.com?subject=${encodeURIComponent("Choptuik-QCD bridge")}`}>
                <Mail className="h-4 w-4 mr-2" /> Contact
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">{t("about.references")}</CardTitle>
          <CardDescription>
            {AUTHOR.name} ({AUTHOR.orcid}) · {AUTHOR.github}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="text-xs space-y-2 text-muted-foreground">
            <li>
              • <span className="text-foreground font-medium">Borsányi et al.</span>, arXiv:1512.04954 —
              lattice QCD estimate of κ_T (extrapolated 95% CL lower bound 2.62; best-fit 8.45).
            </li>
            <li>
              • <span className="text-foreground font-medium">Choptuik (1993)</span> —
              critical exponent δ_C ≈ π/7 in gravitational collapse.
            </li>
            <li>
              • <span className="text-foreground font-medium">Giusti–Rossi–Testa method</span> —
              lattice measurement of F(θ) − F(0), falsification test #1.
            </li>
            <li>
              • <span className="text-foreground font-medium">PSL(2,7) algebraic geometry</span> —
              derivation of the work formula θ̄ = δ_C·N·⟨λ⟩·S_GUE, falsification test #2.
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
