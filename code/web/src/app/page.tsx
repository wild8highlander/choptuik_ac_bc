"use client";

/**
 * page.tsx — Single-page app entry for the Choptuik-QCD bridge.
 *
 * Per the system constraint, only the `/` route is exposed. The view (Home /
 * Section N / About) is selected client-side via the `useNav` hook.
 */

import { useEffect } from "react";
import AppShell from "@/components/layout/AppShell";
import HomeComposite from "@/components/qcd/HomeComposite";
import DashboardView from "@/components/qcd/DashboardView";
import SectionView from "@/components/qcd/SectionView";
import AboutView from "@/components/qcd/AboutView";
import { initNavFromURL, useNav } from "@/lib/qcd/nav";

export default function Page() {
  const { current } = useNav();

  // Sync the in-app nav with the URL ?view=… query on mount. We do not
  // setState here — `initNavFromURL` updates the external store, which
  // `useNav` is subscribed to.
  useEffect(() => {
    initNavFromURL();
  }, []);

  let body: React.ReactNode;
  if (current === "home") {
    body = <HomeComposite />;
  } else if (current === "dashboard") {
    body = <DashboardView />;
  } else if (current === "about") {
    body = <AboutView />;
  } else if (current.startsWith("section:")) {
    const id = Number(current.split(":")[1]);
    body = <SectionView sectionId={id} />;
  } else {
    body = <HomeComposite />;
  }

  return <AppShell>{body}</AppShell>;
}
