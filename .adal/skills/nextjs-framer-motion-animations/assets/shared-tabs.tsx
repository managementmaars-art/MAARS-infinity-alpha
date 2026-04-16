"use client";

import * as React from "react";
import { LayoutGroup, motion } from "motion/react";

export function SharedTabs({
  id,
  items,
  value,
  onChange,
}: {
  id: string;
  items: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <LayoutGroup id={id}>
      <div className="flex gap-4">
        {items.map((item) => {
          const selected = item.value === value;

          return (
            <button
              key={item.value}
              className="relative pb-2"
              onClick={() => onChange(item.value)}
            >
              {item.label}
              {selected ? (
                <motion.div
                  layoutId="underline"
                  className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-current"
                />
              ) : null}
            </button>
          );
        })}
      </div>
    </LayoutGroup>
  );
}
