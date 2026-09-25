"use client";

import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface VerificationStatusProps {
  passed: boolean;
  computing?: boolean;
  description?: string;
  relativeError?: number;
}

export function VerificationStatus({
  passed,
  computing = false,
  description,
  relativeError,
}: VerificationStatusProps) {
  if (computing) {
    return (
      <div className="flex items-center gap-2">
        <Loader2 className="h-4 w-4 text-teal-400 animate-spin" />
        <span className="text-sm text-gray-400">Computing...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {passed ? (
        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
      ) : (
        <XCircle className="h-4 w-4 text-red-400" />
      )}
      <Badge
        variant={passed ? "success" : "destructive"}
        className={cn("transition-all duration-300")}
      >
        {passed ? "PASS" : "FAIL"}
      </Badge>
      {description && (
        <span className="text-xs text-gray-400">{description}</span>
      )}
      {relativeError !== undefined && (
        <span className="text-xs font-mono text-gray-500">
          (ε = {relativeError.toExponential(2)})
        </span>
      )}
    </div>
  );
}
