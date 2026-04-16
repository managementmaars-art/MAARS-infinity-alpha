"use client";

import * as React from "react";
import Link, { LinkProps } from "next/link";
import { motion } from "motion/react";

const LinkButtonBase = React.forwardRef<
  HTMLAnchorElement,
  LinkProps & React.AnchorHTMLAttributes<HTMLAnchorElement>
>(function LinkButtonBase(props, ref) {
  const { href, ...rest } = props;
  return <Link ref={ref} href={href} {...rest} />;
});

const MotionLinkButton = motion.create(LinkButtonBase);

export { MotionLinkButton };
