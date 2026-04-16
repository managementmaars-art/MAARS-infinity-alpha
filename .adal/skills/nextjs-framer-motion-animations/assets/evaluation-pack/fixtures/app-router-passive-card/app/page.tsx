import { ProductCard } from "@/components/product-card"

const products = [
  { id: "lens", title: "Prime Lens", price: "€399", description: "Fast portrait lens." },
  { id: "tripod", title: "Travel Tripod", price: "€149", description: "Lightweight carbon legs." },
  { id: "bag", title: "Camera Bag", price: "€89", description: "Weatherproof everyday carry." }
]

export default function Page() {
  return (
    <main className="grid gap-4 p-8 md:grid-cols-3">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          title={product.title}
          price={product.price}
          description={product.description}
        />
      ))}
    </main>
  )
}
