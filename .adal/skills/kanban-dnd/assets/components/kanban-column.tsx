"use client";

import { useDroppable } from "@dnd-kit/core";
import { KanbanCard } from "./kanban-card";
import { cn } from "@/lib/utils";

// Types - replace with your actual types
interface Card {
  id: string;
  title: string;
  columnId: string;
}

interface Column {
  id: string;
  name: string;
  color: string;
}

interface KanbanColumnProps {
  column: Column;
  cards: Card[];
  onCardClick?: (cardId: string) => void;
  isOver?: boolean;
  isDragging?: boolean;
}

export function KanbanColumn({
  column,
  cards,
  onCardClick,
  isOver = false,
  isDragging = false,
}: KanbanColumnProps) {
  // CRITICAL: Include data.type for collision detection filtering
  const { setNodeRef } = useDroppable({
    id: column.id,
    data: {
      type: "column",
      columnId: column.id,
    },
  });

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "flex-shrink-0 w-72 flex flex-col h-full rounded-xl transition-all duration-200",
        isDragging && "bg-muted/30",
        isOver && "bg-primary/5 ring-2 ring-primary/20 ring-inset"
      )}
    >
      {/* Column header */}
      <div
        className={cn(
          "flex items-center gap-2 mb-3 px-3 py-2 rounded-t-xl transition-colors",
          isOver && "bg-primary/10"
        )}
      >
        <span
          className={cn(
            "w-2.5 h-2.5 rounded-full flex-shrink-0 transition-transform",
            isOver && "scale-125"
          )}
          style={{ backgroundColor: column.color }}
        />
        <h3 className="font-medium text-sm truncate">{column.name}</h3>
        <span
          className={cn(
            "text-xs text-muted-foreground ml-auto tabular-nums bg-muted px-1.5 py-0.5 rounded-md",
            isOver && "bg-primary/20 text-primary"
          )}
        >
          {cards.length}
        </span>
      </div>

      {/* Droppable area */}
      <div
        className={cn(
          "flex-1 min-h-0 px-2 pb-2 transition-all duration-200",
          isOver && "scale-[1.01]"
        )}
      >
        {cards.length === 0 ? (
          <div
            className={cn(
              "flex flex-col items-center justify-center h-full min-h-[200px] text-muted-foreground border-2 border-dashed rounded-lg transition-all duration-200",
              isOver
                ? "border-primary/40 bg-primary/5"
                : "border-border/50"
            )}
          >
            <p className="text-sm font-medium">No items</p>
            <p className="text-xs opacity-60 mt-1">
              {isDragging ? "Drop here" : "Drag items here"}
            </p>
          </div>
        ) : (
          <div className="h-full overflow-y-auto space-y-2 scrollbar-thin">
            {cards.map((card) => (
              <KanbanCard
                key={card.id}
                card={card}
                onClick={() => onCardClick?.(card.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
