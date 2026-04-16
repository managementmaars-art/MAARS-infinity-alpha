type ProductCardProps = {
  title: string
  price: string
  description: string
}

export function ProductCard({ title, price, description }: ProductCardProps) {
  return (
    <article className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
      <div className="mb-3 text-sm text-black/60">{price}</div>
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-sm text-black/70">{description}</p>
    </article>
  )
}
