"use client";

import { useDraggable } from "@dnd-kit/core";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

// Types - replace with your actual types
interface CardData {
  id: string;
  title: string;
  columnId: string;
}

interface KanbanCardProps {
  card: CardData;
  onClick: () => void;
  isDragging?: boolean;
}

export function KanbanCard({
  card,
  onClick,
  isDragging = false,
}: KanbanCardProps) {
  // Use useDraggable for cross-column moves (NOT useSortable)
  const {
    attributes,
    listeners,
    setNodeRef,
    isDragging: isCurrentlyDragging,
  } = useDraggable({
    id: card.id,
    data: {
      type: "card",
      card,
    },
  });

  // isDragging prop is for the DragOverlay copy
  // isCurrentlyDragging is for the original card being dragged
  const isBeingDragged = isDragging || isCurrentlyDragging;

  return (
    <Card
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      className={cn(
        // Base styles
        "p-3 transition-all duration-150",
        // Draggable cursor - entire card is draggable
        "cursor-grab active:cursor-grabbing",
        // Touch support
        "touch-none select-none",
        // Hover state
        "hover:shadow-md hover:border-border/80",
        // Original card being dragged (faded)
        isCurrentlyDragging && "opacity-30",
        // DragOverlay card (elevated, slightly rotated)
        isDragging && "shadow-xl ring-2 ring-primary/20 rotate-[1deg] cursor-grabbing"
      )}
      onClick={(e) => {
        // Don't trigger click if dragging
        if (isBeingDragged) return;
        e.stopPropagation();
        onClick();
      }}
    >
      {/* Card content - customize as needed */}
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">
            {card.title}
          </p>
          {/* Add more card content here */}
        </div>
      </div>
    </Card>
  );
}
