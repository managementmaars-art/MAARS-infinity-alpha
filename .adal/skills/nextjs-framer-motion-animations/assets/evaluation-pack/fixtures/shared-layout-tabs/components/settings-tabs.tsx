"use client"

import { useState } from "react"

export function SettingsTabs({ id, items }: { id: string; items: string[] }) {
  const [active, setActive] = useState(items[0])

  return (
    <div className="flex gap-2 rounded-full border p-1">
      {items.map((item) => {
        const selected = item === active

        return (
          <button
            key={item}
            type="button"
            className="relative rounded-full px-4 py-2 text-sm"
            onClick={() => setActive(item)}
          >
            <span>{item}</span>
            {selected ? <span className="absolute inset-x-2 -bottom-px h-0.5 bg-current" /> : null}
          </button>
        )
      })}
    </div>
  )
}
