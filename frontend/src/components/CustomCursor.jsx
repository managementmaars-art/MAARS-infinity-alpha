import { useEffect, useRef } from "react";

export default function CustomCursor() {
  const dotRef  = useRef(null);
  const ringRef = useRef(null);
  const pos     = useRef({ x: -100, y: -100 });
  const ring    = useRef({ x: -100, y: -100 });
  const raf     = useRef(null);
  const hovered = useRef(false);

  useEffect(() => {
    const onMove = (e) => {
      pos.current = { x: e.clientX, y: e.clientY };
    };

    const onEnter = () => { hovered.current = true; };
    const onLeave = () => { hovered.current = false; };

    // Track hoverable elements
    const addListeners = () => {
      document.querySelectorAll("a, button, [data-cursor]").forEach(el => {
        el.addEventListener("mouseenter", onEnter);
        el.addEventListener("mouseleave", onLeave);
      });
    };
    addListeners();

    window.addEventListener("mousemove", onMove);

    // Observer for dynamically added elements
    const observer = new MutationObserver(addListeners);
    observer.observe(document.body, { childList: true, subtree: true });

    const animate = () => {
      if (dotRef.current && ringRef.current) {
        // Dot: instant
        dotRef.current.style.transform = `translate(${pos.current.x - 4}px, ${pos.current.y - 4}px)`;

        // Ring: laggy lerp
        ring.current.x += (pos.current.x - ring.current.x) / 8;
        ring.current.y += (pos.current.y - ring.current.y) / 8;

        const scale = hovered.current ? 2.2 : 1;
        ringRef.current.style.transform =
          `translate(${ring.current.x - 18}px, ${ring.current.y - 18}px) scale(${scale})`;
        ringRef.current.style.opacity = hovered.current ? "0.5" : "0.25";
      }
      raf.current = requestAnimationFrame(animate);
    };
    raf.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("mousemove", onMove);
      cancelAnimationFrame(raf.current);
      observer.disconnect();
    };
  }, []);

  return (
    <>
      {/* Inner dot */}
      <div
        ref={dotRef}
        style={{
          position: "fixed", top: 0, left: 0, zIndex: 9999,
          width: 8, height: 8, borderRadius: "50%",
          background: "#4fd1c5",
          pointerEvents: "none",
          willChange: "transform",
          mixBlendMode: "difference",
        }}
      />
      {/* Outer ring */}
      <div
        ref={ringRef}
        style={{
          position: "fixed", top: 0, left: 0, zIndex: 9998,
          width: 36, height: 36, borderRadius: "50%",
          border: "1px solid #4fd1c5",
          pointerEvents: "none",
          willChange: "transform, opacity",
          transition: "opacity 0.2s, transform 0.08s",
          mixBlendMode: "difference",
        }}
      />
    </>
  );
}
