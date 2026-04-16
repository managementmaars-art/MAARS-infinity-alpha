import { SettingsDrawer } from "@/components/settings-drawer"

export default function SettingsPage() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <SettingsDrawer initialOpen={false} />
    </main>
  )
}
