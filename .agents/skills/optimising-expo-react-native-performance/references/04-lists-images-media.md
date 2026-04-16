# Lists, images, and media performance

## Lists: the highest-ROI surface area

Large lists are a common “everything feels slow” amplifier:
- They increase render cost.
- They create re-render storms.
- They often include images (decode + cache pressure).

## FlatList / VirtualizedList fundamentals

### Always do these first

- Stable `keyExtractor`.
- Avoid re-creating `renderItem` every render.
- Avoid passing new object/array props to every row.
- Keep row components pure and memo-friendly.

### Add `getItemLayout` when item heights are known

If your rows are fixed height (or can be treated as fixed height), `getItemLayout` is a major win.

```tsx
const ITEM_HEIGHT = 72;

<FlatList
  data={data}
  keyExtractor={(item) => item.id}
  getItemLayout={(_, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  renderItem={renderItem}
/>;
```

### Tune the window (measure trade-offs)

Knobs you may adjust (carefully):
- `initialNumToRender`
- `windowSize`
- `maxToRenderPerBatch`
- `updateCellsBatchingPeriod`
- `removeClippedSubviews` (often helps, but can cause bugs in complex layouts)

Trade-off:
- Smaller windows reduce memory and render cost, but can cause blanking when scrolling fast.

## When to switch to FlashList (or similar)

If you have:
- Thousands of items,
- Heterogeneous row types,
- Very heavy rows,

…then a performance-optimised list library can be a step-change improvement.

### FlashList baseline config

```tsx
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={data}
  estimatedItemSize={72}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}
  getItemType={(item) => item.type}
/>;
```

FlashList success factors:
- Don’t benchmark in dev mode.
- Provide `estimatedItemSize`.
- Provide `getItemType` for heterogeneous rows.
- Memoise props aggressively for row stability.

## Images: use a native pipeline, control caching

### Prefer `expo-image` for image-heavy UIs

It provides:
- Disk + memory caching
- Placeholders (BlurHash/ThumbHash)
- Smooth transitions (avoid flicker)

Example:

```tsx
import { Image } from 'expo-image';

<Image
  source={{ uri: url }}
  style={{ width: 96, height: 96 }}
  contentFit="cover"
  placeholder={{ blurhash }}
  transition={150}
/>;
```

Operational guidance:
- Decide a cache policy (disk vs memory) based on your UX.
- Prefetch images for the next screen when it’s cheap.
- For grids/feeds: ensure stable sizing to avoid relayout.

## Video: caching and its limitations

### Prefer `expo-video` (expo-av Video is deprecated)

`expo-video` supports caching (LRU policy), but note limitations:
- On iOS, caching may not work for HLS sources.
- DRM-protected content may not be cacheable.

Example:

```ts
import { VideoView, useVideoPlayer } from 'expo-video';

const player = useVideoPlayer(
  { uri: videoUrl, useCaching: true },
  (p) => {
    p.loop = true;
    p.play();
  }
);
```

Operational guidance:
- Cache only replay-heavy media.
- Provide a “clear cache” option if storage pressure is plausible.

## Debugging checklist for list/image jank

- Is the list virtualised (FlatList/FlashList), not ScrollView?
- Are row components re-rendering unnecessarily?
- Are images decoding at render time (no caching/placeholder)?
- Is there heavy overdraw (text over images, translucent layers)?
- Is UI thread FPS dropping even when JS is quiet?

## Links

See `references/resources.md` for:
- React Native FlatList optimisation docs
- FlashList docs
- Expo Image and Video docs
