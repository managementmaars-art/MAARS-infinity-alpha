export default function TeamPage({ params }: { params: { team: string } }) {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold">Team {params.team}</h1>
      <p className="text-sm text-white/70">Metrics and recent changes for this team.</p>
    </section>
  )
}
