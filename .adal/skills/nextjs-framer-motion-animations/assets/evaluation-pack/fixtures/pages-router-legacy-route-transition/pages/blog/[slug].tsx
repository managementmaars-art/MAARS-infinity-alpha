import { useRouter } from "next/router"

export default function BlogPostPage() {
  const router = useRouter()

  return (
    <main className="p-8">
      <h1 className="text-3xl font-semibold">{router.query.slug}</h1>
      <p className="mt-3 text-sm text-black/70">
        Blog content lives here and navigates between dynamic slugs.
      </p>
    </main>
  )
}
