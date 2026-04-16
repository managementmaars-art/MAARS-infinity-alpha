// Motion package only.
// Use this in App Router when a passive Motion component is enough and you do
// not need Motion hooks or other client-only logic.

import * as motion from "motion/react-client";

export function MotionCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.article
      className={className}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
    >
      {children}
    </motion.article>
  );
}
