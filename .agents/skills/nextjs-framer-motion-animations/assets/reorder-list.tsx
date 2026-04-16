"use client";

import * as React from "react";
import { Reorder } from "motion/react";

export function ReorderList({
  initialItems,
}: {
  initialItems: string[];
}) {
  const [items, setItems] = React.useState(initialItems);

  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item key={item} value={item}>
          {item}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
}
