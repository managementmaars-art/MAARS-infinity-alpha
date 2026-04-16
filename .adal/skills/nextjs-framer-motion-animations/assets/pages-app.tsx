import type { AppProps } from "next/app";
import { AnimatePresence, MotionConfig } from "motion/react";

export default function App({ Component, pageProps, router }: AppProps) {
  return (
    <MotionConfig reducedMotion="user">
      <AnimatePresence initial={false} mode="wait">
        <Component {...pageProps} key={router.asPath} />
      </AnimatePresence>
    </MotionConfig>
  );
}
