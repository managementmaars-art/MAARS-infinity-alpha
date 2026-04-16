"use client"

import { useState } from "react"

export function SettingsDrawer({ initialOpen = false }: { initialOpen?: boolean }) {
  const [open, setOpen] = useState(initialOpen)

  return (
    <section className="mt-6">
      <button
        type="button"
        className="rounded-md border px-4 py-2"
        onClick={() => setOpen((value) => !value)}
      >
        {open ? "Close settings" : "Open settings"}
      </button>

      {open ? (
        <aside className="mt-4 rounded-xl border bg-white p-6 shadow-xl">
          <h2 className="text-lg font-semibold">Panel</h2>
          <p className="mt-2 text-sm text-black/70">
            Toggle preferences, notifications, and account details here.
          </p>
        </aside>
      ) : null}
    </section>
  )
}
