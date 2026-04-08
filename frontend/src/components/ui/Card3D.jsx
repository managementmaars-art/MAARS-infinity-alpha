import { use3DTilt } from "../../hooks/use3DTilt";

/**
 * Card3D — wraps any content with interactive 3D perspective tilt.
 * Props: strength(12), scale(1.02), lift(8), glare(true), children, style, className
 */
export default function Card3D({ children, strength = 12, scale = 1.02, lift = 8, glare = true, style = {}, className = "" }) {
  const ref = use3DTilt({ strength, scale, lift });

  return (
    <div
      ref={ref}
      className={className}
      style={{
        position: "relative",
        transformStyle: "preserve-3d",
        willChange: "transform",
        ...style,
      }}
    >
      {children}
      {/* Holographic glare overlay */}
      {glare && (
        <div style={{
          position: "absolute", inset: 0, borderRadius: "inherit",
          background: "radial-gradient(circle at var(--shimmer-x, 50%) var(--shimmer-y, 50%), rgba(255,255,255,0.06) 0%, transparent 60%)",
          pointerEvents: "none", zIndex: 100,
          transition: "background 0.05s ease",
        }} />
      )}
    </div>
  );
}
