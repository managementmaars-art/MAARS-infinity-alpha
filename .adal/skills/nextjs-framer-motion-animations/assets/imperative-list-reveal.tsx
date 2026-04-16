"use client";

import * as React from "react";
import { useAnimate, useInView, stagger } from "motion/react";

export function ImperativeListReveal({
  children,
}: {
  children: React.ReactNode;
}) {
  const [scope, animate] = useAnimate();
  const inView = useInView(scope, { once: true, amount: 0.2 });

  React.useEffect(() => {
    if (!inView) return;

    void animate(
      "li",
      { opacity: [0, 1], y: [12, 0] },
      {
        delay: stagger(0.06),
        duration: 0.24,
        ease: [0.22, 1, 0.36, 1],
      },
    );
  }, [animate, inView]);

  return <ul ref={scope}>{children}</ul>;
}
