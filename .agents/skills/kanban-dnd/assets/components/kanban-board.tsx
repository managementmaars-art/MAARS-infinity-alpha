"use client";

import { useMemo, useState, useCallback } from "react";
import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
  type DragOverEvent,
  type UniqueIdentifier,
} from "@dnd-kit/core";
import { sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import { snapCenterToCursor } from "@dnd-kit/modifiers";
import { KanbanColumn } from "./kanban-column";
import { KanbanCard } from "./kanban-card";
import { columnPriorityCollision } from "@/lib/dnd/collision-detection";
import { toast } from "sonner";

// Types - replace with your actual types
interface Card {
  id: string;
  title: string;
  columnId: string;
  // ... other fields
}

interface Column {
  id: string;
  name: string;
  color: string;
}

interface KanbanBoardProps {
  columns: Column[];
  cards: Card[];
  onCardMove: (cardId: string, newColumnId: string) => Promise<void>;
  onCardClick?: (cardId: string) => void;
}

export function KanbanBoard({
  columns,
  cards,
  onCardMove,
  onCardClick,
}: KanbanBoardProps) {
  const [activeCard, setActiveCard] = useState<Card | null>(null);
  const [activeOverColumn, setActiveOverColumn] = useState<string | null>(null);

  // Sensors with small distance threshold for responsive feel
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Map card ID to column ID for quick lookups
  const cardColumnMap = useMemo(() => {
    const map = new Map<string, string>();
    cards.forEach((card) => {
      map.set(card.id, card.columnId);
    });
    return map;
  }, [cards]);

  // Group cards by column
  const cardsByColumn = useMemo(() => {
    const grouped = new Map<string, Card[]>();
    
    // Initialize all columns with empty arrays
    columns.forEach((column) => {
      grouped.set(column.id, []);
    });

    // Group cards by their columnId
    cards.forEach((card) => {
      const columnCards = grouped.get(card.columnId) || [];
      columnCards.push(card);
      grouped.set(card.columnId, columnCards);
    });

    return grouped;
  }, [cards, columns]);

  // Set of column IDs for quick lookup
  const columnIds = useMemo(() => {
    return new Set(columns.map((c) => c.id));
  }, [columns]);

  // Resolve drop target to column ID (handles both column and card drops)
  const findTargetColumnId = useCallback(
    (overId: UniqueIdentifier | undefined): string | null => {
      if (!overId) return null;
      
      const overIdStr = String(overId);
      
      // Check if it's a column ID directly
      if (columnIds.has(overIdStr)) {
        return overIdStr;
      }
      
      // Otherwise it's a card ID - find which column that card is in
      const columnId = cardColumnMap.get(overIdStr);
      return columnId || null;
    },
    [columnIds, cardColumnMap]
  );

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const { active } = event;
    const card = cards.find((c) => c.id === active.id);
    if (card) {
      setActiveCard(card);
      setActiveOverColumn(card.columnId);
    }
  }, [cards]);

  const handleDragOver = useCallback((event: DragOverEvent) => {
    const { over } = event;
    if (!over) {
      setActiveOverColumn(null);
      return;
    }
    
    const targetColumnId = findTargetColumnId(over.id);
    setActiveOverColumn(targetColumnId);
  }, [findTargetColumnId]);

  const handleDragEnd = useCallback(async (event: DragEndEvent) => {
    const { active, over } = event;
    
    setActiveCard(null);
    setActiveOverColumn(null);

    if (!over) return;

    const cardId = String(active.id);
    const targetColumnId = findTargetColumnId(over.id);

    if (!targetColumnId) return;

    const card = cards.find((c) => c.id === cardId);
    if (!card || card.columnId === targetColumnId) return;

    // Move the card
    try {
      await onCardMove(cardId, targetColumnId);
    } catch (error) {
      toast.error("Failed to move card", {
        description: error instanceof Error ? error.message : "Unknown error",
      });
    }
  }, [cards, findTargetColumnId, onCardMove]);

  const handleDragCancel = useCallback(() => {
    setActiveCard(null);
    setActiveOverColumn(null);
  }, []);

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={columnPriorityCollision}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      {/* Kanban columns */}
      <div className="flex h-full gap-4 overflow-x-auto pb-4">
        {columns.map((column) => (
          <KanbanColumn
            key={column.id}
            column={column}
            cards={cardsByColumn.get(column.id) || []}
            onCardClick={onCardClick}
            isOver={activeOverColumn === column.id}
            isDragging={!!activeCard}
          />
        ))}
      </div>

      {/* Drag overlay - follows cursor, no drop animation */}
      <DragOverlay
        modifiers={[snapCenterToCursor]}
        dropAnimation={null}
      >
        {activeCard ? (
          <div className="w-[272px] pointer-events-none">
            <KanbanCard
              card={activeCard}
              onClick={() => {}}
              isDragging
            />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
