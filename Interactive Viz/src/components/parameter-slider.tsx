"use client";

import { Slider } from "@/components/ui/slider";

interface ParameterSliderProps {
  label: string;
  symbol: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  formatValue?: (v: number) => string;
}

export function ParameterSlider({
  label,
  symbol,
  value,
  min,
  max,
  step,
  onChange,
  formatValue,
}: ParameterSliderProps) {
  const displayValue = formatValue ? formatValue(value) : value.toFixed(4);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-300">
          <span className="font-mono text-teal-400 mr-1">{symbol}</span>
          {label}
        </label>
        <span className="text-sm font-mono text-white bg-navy-700 px-2 py-0.5 rounded">
          {displayValue}
        </span>
      </div>
      <Slider
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={(v) => onChange(v[0])}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-gray-500 font-mono">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}
