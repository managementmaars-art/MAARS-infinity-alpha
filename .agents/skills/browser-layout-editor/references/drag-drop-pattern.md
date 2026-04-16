# Cross-Container Drag-and-Drop Pattern

Complete implementation for dragging items between multiple SVG containers with a ghost element.

## The Problem

Items rendered inside separate SVG elements cannot visually move across SVG boundaries. When dragging from Sheet 1 to Sheet 2, the item stays visually "stuck" at Sheet 1's edge.

## The Solution: Ghost Element

Create a DOM element (div) that:
1. Follows the cursor globally (outside any SVG)
2. Shows what's being dragged
3. Gets removed on drop

## Complete Implementation

### CSS

```css
.drag-ghost {
    position: fixed;
    pointer-events: none;
    opacity: 0.7;
    z-index: 1000;
    border: 2px solid #fff;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    overflow: hidden;
}

.container-wrapper.drag-over {
    outline: 3px dashed #4ECDC4;
    outline-offset: -3px;
}
```

### JavaScript State

```javascript
let dragState = null;
let dragGhost = null;
let scale = 0.35;  // SVG to screen scale factor
```

### Create Ghost Function

```javascript
function createDragGhost(item, color) {
    const ghost = document.createElement('div');
    ghost.className = 'drag-ghost';
    ghost.style.width = (item.width * scale) + 'px';
    ghost.style.height = (item.height * scale) + 'px';
    ghost.style.background = color;
    ghost.style.color = '#333';
    ghost.textContent = item.name.slice(0, 12);
    document.body.appendChild(ghost);
    return ghost;
}
```

### Mouse Down Handler

```javascript
function onMouseDown(e) {
    if (e.button !== 0) return;  // Left click only

    const containerIdx = parseInt(e.target.dataset.container);
    const itemIdx = parseInt(e.target.dataset.item);
    const item = layout.containers[containerIdx].items[itemIdx];
    const svg = e.target.closest('svg');
    const color = COLORS[itemIdx % COLORS.length];

    dragState = {
        containerIdx,
        itemIdx,
        startX: e.clientX,
        startY: e.clientY,
        origX: item.x,
        origY: item.y,
        moved: false,
        itemWidth: item.width,
        itemHeight: item.height,
        color
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    e.preventDefault();
}
```

### Mouse Move Handler

```javascript
function onMouseMove(e) {
    if (!dragState) return;

    const dx = e.clientX - dragState.startX;
    const dy = e.clientY - dragState.startY;

    // Detect significant movement
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        dragState.moved = true;

        // Create ghost on first significant move
        if (!dragGhost) {
            const item = layout.containers[dragState.containerIdx].items[dragState.itemIdx];
            dragGhost = createDragGhost(item, dragState.color);
        }
    }

    // Position ghost centered on cursor
    if (dragGhost) {
        dragGhost.style.left = (e.clientX - dragState.itemWidth * scale / 2) + 'px';
        dragGhost.style.top = (e.clientY - dragState.itemHeight * scale / 2) + 'px';
    }

    // Highlight container under cursor
    document.querySelectorAll('.container-wrapper').forEach(wrapper => {
        const rect = wrapper.getBoundingClientRect();
        const over = e.clientX >= rect.left && e.clientX <= rect.right &&
                     e.clientY >= rect.top && e.clientY <= rect.bottom;
        wrapper.classList.toggle('drag-over', over);
    });
}
```

### Mouse Up Handler

```javascript
async function onMouseUp(e) {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);

    // Remove ghost
    if (dragGhost) {
        dragGhost.remove();
        dragGhost = null;
    }

    // Remove highlights
    document.querySelectorAll('.container-wrapper').forEach(w =>
        w.classList.remove('drag-over')
    );

    if (!dragState || !dragState.moved) {
        dragState = null;
        return;
    }

    // Find target container
    let targetContainer = -1;
    let targetSvg = null;

    document.querySelectorAll('.container-wrapper').forEach(wrapper => {
        const svg = wrapper.querySelector('svg');
        const rect = svg.getBoundingClientRect();
        const over = e.clientX >= rect.left && e.clientX <= rect.right &&
                     e.clientY >= rect.top && e.clientY <= rect.bottom;
        if (over) {
            targetContainer = parseInt(wrapper.dataset.containerIdx);
            targetSvg = svg;
        }
    });

    // Cancel if not dropped on a container
    if (targetContainer === -1) {
        render();
        dragState = null;
        return;
    }

    // Calculate drop position relative to TARGET SVG
    const item = layout.containers[dragState.containerIdx].items[dragState.itemIdx];
    const targetRect = targetSvg.getBoundingClientRect();
    const config = layout.config;

    // Convert screen coords to container coords, center on cursor
    let dropX = Math.round((e.clientX - targetRect.left) / scale - item.width / 2);
    let dropY = Math.round((e.clientY - targetRect.top) / scale - item.height / 2);

    // Clamp to bounds
    dropX = Math.max(0, Math.min(dropX, config.containerWidth - item.width));
    dropY = Math.max(0, Math.min(dropY, config.containerHeight - item.height));

    if (targetContainer !== dragState.containerIdx) {
        // Move to different container via API
        await movePiece(dragState.containerIdx, dragState.itemIdx, targetContainer, dropX, dropY);
        layout = await fetchLayout();
        render();
    } else {
        // Update position on same container
        await updatePiece(dragState.containerIdx, dragState.itemIdx, { x: dropX, y: dropY });
        item.x = dropX;
        item.y = dropY;
        render();
    }

    dragState = null;
}
```

## Coordinate Transform Explanation

The key formula for cross-container drops:

```javascript
// e.clientX/Y = mouse position in viewport (screen pixels)
// targetRect.left/top = SVG position in viewport (screen pixels)
// scale = ratio of screen pixels to container units

// Step 1: Get mouse position relative to target SVG (in screen pixels)
const screenX = e.clientX - targetRect.left;
const screenY = e.clientY - targetRect.top;

// Step 2: Convert to container units
const containerX = screenX / scale;
const containerY = screenY / scale;

// Step 3: Center the item on cursor (offset by half item size)
const dropX = containerX - item.width / 2;
const dropY = containerY - item.height / 2;

// Step 4: Clamp to container bounds
const finalX = Math.max(0, Math.min(dropX, containerWidth - item.width));
const finalY = Math.max(0, Math.min(dropY, containerHeight - item.height));
```

## API Endpoint for Cross-Container Move

```python
@app.post("/api/move-piece")
async def move_piece(request: MoveRequest) -> Response:
    # Remove from source
    item = containers[request.from_container].items.pop(request.item_index)

    # Update position
    item.x = request.x
    item.y = request.y

    # Add to target
    containers[request.to_container].items.append(item)

    # Recalculate utilizations
    recalc_utilization(containers[request.from_container])
    recalc_utilization(containers[request.to_container])

    return {"success": True}
```

## Tips

1. **Scale consistency**: Use the same `scale` value for rendering and coordinate conversion
2. **Ghost size**: Match the ghost size to the scaled item size for visual accuracy
3. **Pointer events**: Set `pointer-events: none` on ghost so it doesn't interfere with drop detection
4. **Bounds clamping**: Always clamp to prevent items from going outside container
5. **Reload on cross-move**: After moving between containers, reload the full layout to ensure consistency
