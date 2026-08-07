"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  CheckCircle2,
  SlidersHorizontal,
  Grid3X3,
  Layers,
  Radio,
  FlaskConical,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/verify", label: "Verification", icon: CheckCircle2 },
  { href: "/simulate", label: "Simulation", icon: SlidersHorizontal },
  { href: "/structures", label: "Structures", icon: Grid3X3 },
  { href: "/surfaces", label: "Surfaces", icon: Layers },
  { href: "/qnm", label: "QNM / LIGO", icon: Radio },
  { href: "/hypothesis", label: "Hypothesis", icon: FlaskConical },
  { href: "/reports", label: "Reports", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 min-h-screen bg-navy-950 border-r border-navy-700 flex flex-col">
      <div className="p-4 border-b border-navy-700">
        <h1 className="text-sm font-bold text-teal-400 tracking-tight">
          CHOPTYUK
        </h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Spinor Monograph Viz
        </p>
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-all",
                active
                  ? "bg-teal-600/20 text-teal-400 font-medium"
                  : "text-gray-400 hover:bg-navy-800 hover:text-gray-200"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-navy-700">
        <p className="text-[10px] text-gray-600 font-mono">
          Klein quartic · PSL(2,7) · 168
        </p>
      </div>
    </aside>
  );
}
