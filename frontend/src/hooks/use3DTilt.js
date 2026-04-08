import { useEffect, useRef } from "react";

/**
 * Applies interactive perspective tilt to a DOM element on mousemove.
 * Returns a ref to attach to the element.
 */
export function use3DTilt({ strength = 12, scale = 1.02, perspective = 1000, lift = 8 } = {}) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const onMove = (e) => {
      const rect = el.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width  - 0.5) * 2;
      const y = ((e.clientY - rect.top)  / rect.height - 0.5) * 2;
      el.style.transform = `perspective(${perspective}px) rotateX(${-y * strength}deg) rotateY(${x * strength}deg) translateZ(${lift}px) scale(${scale})`;
      el.style.transition = "transform 0.05s ease-out";
      // Dynamic shimmer via CSS variable
      el.style.setProperty("--shimmer-x", `${(x + 1) / 2 * 100}%`);
      el.style.setProperty("--shimmer-y", `${(y + 1) / 2 * 100}%`);
    };

    const onLeave = () => {
      el.style.transform = `perspective(${perspective}px) rotateX(0deg) rotateY(0deg) translateZ(0px) scale(1)`;
      el.style.transition = "transform 0.4s cubic-bezier(0.22,1,0.36,1)";
    };

    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
    return () => {
      el.removeEventListener("mousemove", onMove);
      el.removeEventListener("mouseleave", onLeave);
    };
  }, [strength, scale, perspective, lift]);

  return ref;
}
