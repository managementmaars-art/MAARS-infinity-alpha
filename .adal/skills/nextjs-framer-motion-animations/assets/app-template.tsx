import * as React from "react";
import { FadeInOnMount } from "@/components/motion/fade-in-on-mount";

export default function Template({
  children,
}: {
  children: React.ReactNode;
}) {
  return <FadeInOnMount>{children}</FadeInOnMount>;
}
