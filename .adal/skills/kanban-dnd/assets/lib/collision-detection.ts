import {
  pointerWithin,
  rectIntersection,
  type CollisionDetection,
} from "@dnd-kit/core";

/**
 * Custom collision detection that prioritizes column droppables over cards.
 * 
 * This is critical for kanban boards where cards are inside columns.
 * Without this, dropping on a card returns the card's ID instead of the column's ID.
 * 
 * The collision detection:
 * 1. First checks pointer intersections for columns (most accurate)
 * 2. Falls back to rect intersection for columns (catches edge cases)
 * 3. Returns any collision as last resort
 * 
 * Columns must include `data: { type: "column" }` in their useDroppable config.
 */
export const columnPriorityCollision: CollisionDetection = (args) => {
  // First, check for pointer intersections with columns
  const pointerCollisions = pointerWithin(args);
  
  // Filter to only get column collisions (columns have data.type === 'column')
  const columnCollisions = pointerCollisions.filter(
    (collision) => collision.data?.droppableContainer?.data?.current?.type === "column"
  );

  if (columnCollisions.length > 0) {
    return columnCollisions;
  }

  // Fallback to rect intersection for broader detection
  const rectCollisions = rectIntersection(args);
  const columnRectCollisions = rectCollisions.filter(
    (collision) => collision.data?.droppableContainer?.data?.current?.type === "column"
  );

  if (columnRectCollisions.length > 0) {
    return columnRectCollisions;
  }

  return rectCollisions;
};
