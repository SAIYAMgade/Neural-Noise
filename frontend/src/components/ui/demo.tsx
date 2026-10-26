"use client";

import { NeuralNoise } from "@/components/ui/neural-noise";

export default function DemoOne() {
  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center overflow-hidden bg-black min-h-[400px]">
      <NeuralNoise />
      <span className="pointer-events-none absolute z-10 text-center text-7xl leading-none font-semibold tracking-tighter whitespace-pre-wrap text-rose-500 select-none">
        Neural Noise
      </span>
    </div>
  );
}
