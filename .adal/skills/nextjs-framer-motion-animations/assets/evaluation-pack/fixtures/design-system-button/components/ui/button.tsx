"use client"

import * as React from "react"

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className = "", ...props },
  ref
) {
  return (
    <button
      {...props}
      ref={ref}
      className={[
        "inline-flex items-center justify-center rounded-lg bg-black px-4 py-2 text-white",
        className
      ].join(" ")}
    />
  )
})
