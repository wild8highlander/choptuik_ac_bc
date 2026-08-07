"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { VerificationStatus } from "@/components/verification-status";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { runVerification } from "@/lib/compute";
import type { VerificationEntry } from "@/lib/types";
import { useState, useEffect, useCallback } from "react";
import { Play, RotateCcw, CheckCircle2, XCircle, Loader2 } from "lucide-react";

export default function VerifyPage() {
  const [results, setResults] = useState<VerificationEntry[]>([]);
  const [computing, setComputing] = useState<Set<string>>(new Set());
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  const [running, setRunning] = useState(false);
  const [allResults, setAllResults] = useState<VerificationEntry[]>([]);

  const allChecks = runVerification();

  const runAnimatedVerification = useCallback(() => {
    setRunning(true);
    setResults([]);
    setCompleted(new Set());
    setComputing(new Set());
    setAllResults([]);

    let idx = 0;
    const interval = setInterval(() => {
      if (idx >= allChecks.length) {
        clearInterval(interval);
        setRunning(false);
        setComputing(new Set());
        return;
      }

      const check = allChecks[idx];
      setComputing(new Set([check.id]));
      setResults((prev) => [...prev, check]);
      setCompleted((prev) => new Set([...prev, check.id]));
      setAllResults((prev) => [...prev, check]);
      idx++;
    }, 400);

    return () => clearInterval(interval);
  }, [allChecks]);

  useEffect(() => {
    runAnimatedVerification();
  }, []);

  const passCount = results.filter((v) => v.passed).length;
  const failCount = results.filter((v) => !v.passed).length;

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Verification</h1>
          <p className="text-sm text-gray-400 mt-1">
            Live computation of all mathematical identities and reference values
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={runAnimatedVerification}
            disabled={running}
          >
            <RotateCcw className="h-4 w-4 mr-1" />
            Re-run
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle2 className="h-8 w-8 text-emerald-400" />
            <div>
              <p className="text-2xl font-bold text-emerald-400">{passCount}</p>
              <p className="text-xs text-gray-400">Passed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <XCircle className="h-8 w-8 text-red-400" />
            <div>
              <p className="text-2xl font-bold text-red-400">{failCount}</p>
              <p className="text-xs text-gray-400">Failed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <Loader2
              className={`h-8 w-8 text-teal-400 ${running ? "animate-spin" : ""}`}
            />
            <div>
              <p className="text-2xl font-bold text-teal-400">
                {results.length}/{allChecks.length}
              </p>
              <p className="text-xs text-gray-400">Computed</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Results Table */}
      <Card>
        <CardHeader>
          <CardTitle>Computation Results</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]">#</TableHead>
                <TableHead>Identity</TableHead>
                <TableHead className="text-right">Computed</TableHead>
                <TableHead className="text-right">Expected</TableHead>
                <TableHead className="text-right">|Δ|</TableHead>
                <TableHead className="text-right">ε_rel</TableHead>
                <TableHead className="text-center">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allChecks.map((check, idx) => {
                const isComputing = computing.has(check.id);
                const isDone = completed.has(check.id);
                const isPending = !isDone && !isComputing;
                const result = results.find((r) => r.id === check.id);

                return (
                  <TableRow
                    key={check.id}
                    className={`transition-all duration-300 ${
                      isPending ? "opacity-30" : isComputing ? "bg-teal-900/20" : ""
                    }`}
                  >
                    <TableCell className="font-mono text-xs text-gray-500">
                      {idx + 1}
                    </TableCell>
                    <TableCell className="font-mono text-sm text-gray-300">
                      {check.description}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {isPending ? (
                        <span className="text-gray-600">—</span>
                      ) : isComputing ? (
                        <Loader2 className="h-4 w-4 text-teal-400 animate-spin inline" />
                      ) : (
                        <span className="text-white">
                          {result?.computed.toPrecision(8)}
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm text-gray-400">
                      {check.expected.toPrecision(8)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {result ? (
                        <span
                          className={
                            result.passed ? "text-emerald-400" : "text-red-400"
                          }
                        >
                          {result.deviation.toExponential(3)}
                        </span>
                      ) : (
                        <span className="text-gray-600">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {result ? (
                        <span
                          className={
                            result.relativeError < 0.01
                              ? "text-emerald-400"
                              : result.relativeError < 0.1
                              ? "text-amber-400"
                              : "text-red-400"
                          }
                        >
                          {result.relativeError.toExponential(3)}
                        </span>
                      ) : (
                        <span className="text-gray-600">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      {isPending ? (
                        <Badge variant="secondary">Pending</Badge>
                      ) : isComputing ? (
                        <Badge variant="default" className="animate-pulse-glow">
                          Computing
                        </Badge>
                      ) : result ? (
                        <VerificationStatus
                          passed={result.passed}
                          relativeError={result.relativeError}
                        />
                      ) : null}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
