"use client";

/**
 * HomeComposite.tsx — Home view + side panel with ParamPanel + ReportPanel.
 *
 * The Home view shows the 9 section cards; the side panel lets the user
 * configure a custom run and download reports immediately.
 */

import HomeView from "./HomeView";
import ParamPanel from "./ParamPanel";
import ReportPanel from "./ReportPanel";

export default function HomeComposite() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <HomeView />
      </div>
      <div className="space-y-4">
        <ParamPanel />
        <ReportPanel />
      </div>
    </div>
  );
}
