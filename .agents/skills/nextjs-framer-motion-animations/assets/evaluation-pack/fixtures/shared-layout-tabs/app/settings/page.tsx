import { SettingsTabs } from "@/components/settings-tabs"

export default function SettingsPage() {
  const items = ["General", "Billing", "Security"]

  return (
    <main className="space-y-10 p-8">
      <SettingsTabs id="primary" items={items} />
      <SettingsTabs id="secondary" items={items} />
    </main>
  )
}
