# React Performance Patterns

Framework-agnostic React patterns for performance optimization.

## Code Splitting

### React.lazy and Suspense

```jsx
import { lazy, Suspense } from 'react';

// Split heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));
const DataTable = lazy(() => import('./DataTable'));

function Dashboard() {
  return (
    <div>
      <Header /> {/* Always loaded */}

      <Suspense fallback={<ChartSkeleton />}>
        <HeavyChart />
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <DataTable />
      </Suspense>
    </div>
  );
}
```

### Route-Level Splitting

```jsx
// With React Router
const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

### Named Exports with lazy

```jsx
// If component uses named export:
const MyComponent = lazy(() =>
  import('./MyComponent').then(module => ({
    default: module.MyComponent
  }))
);
```

## Hydration Optimization

### Avoiding Hydration Mismatches

```jsx
// Problem: Server/client render different content
function Timestamp() {
  // Bad: Different on server vs client
  return <span>{Date.now()}</span>;
}

// Solution: Client-only rendering
function Timestamp() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span>Loading...</span>; // Same as server
  }

  return <span>{Date.now()}</span>;
}
```

### Progressive Hydration Pattern

```jsx
// Defer hydration of non-critical content
function LazyHydrate({ children, whenIdle = false, whenVisible = false }) {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (whenIdle) {
      requestIdleCallback(() => setHydrated(true));
    } else if (whenVisible) {
      const observer = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) {
          setHydrated(true);
          observer.disconnect();
        }
      });
      // Observe wrapper element
    } else {
      setHydrated(true);
    }
  }, [whenIdle, whenVisible]);

  if (!hydrated) {
    return <div dangerouslySetInnerHTML={{ __html: '' }} />;
  }

  return children;
}

// Usage
<LazyHydrate whenVisible>
  <BelowFoldContent />
</LazyHydrate>
```

## Re-render Optimization

### memo for Expensive Components

```jsx
import { memo } from 'react';

// Only re-renders if props change
const ExpensiveList = memo(function ExpensiveList({ items }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
});

// Custom comparison for complex props
const Chart = memo(
  function Chart({ data, config }) {
    // Expensive render
  },
  (prevProps, nextProps) => {
    return (
      prevProps.data.length === nextProps.data.length &&
      prevProps.config.type === nextProps.config.type
    );
  }
);
```

### useCallback for Stable References

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // Bad: New function every render
  const handleClick = () => console.log('clicked');

  // Good: Stable reference
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  return <MemoizedChild onClick={handleClick} />;
}
```

### useMemo for Expensive Calculations

```jsx
function DataView({ items, filter }) {
  // Bad: Recalculates every render
  const filtered = items.filter(item => item.type === filter);

  // Good: Only recalculates when dependencies change
  const filtered = useMemo(
    () => items.filter(item => item.type === filter),
    [items, filter]
  );

  return <List items={filtered} />;
}
```

### Avoid Inline Objects/Arrays in JSX

```jsx
// Bad: New object every render, breaks memo
<MemoizedComponent style={{ color: 'red' }} />
<MemoizedComponent items={[1, 2, 3]} />

// Good: Stable references
const style = useMemo(() => ({ color: 'red' }), []);
const items = useMemo(() => [1, 2, 3], []);
<MemoizedComponent style={style} />
<MemoizedComponent items={items} />

// Or define outside component if truly static
const staticStyle = { color: 'red' };
const staticItems = [1, 2, 3];
```

## Event Handler Optimization

### Debounce/Throttle Handlers

```jsx
import { useMemo } from 'react';
import { debounce, throttle } from 'lodash-es';

function SearchInput({ onSearch }) {
  const debouncedSearch = useMemo(
    () => debounce(onSearch, 300),
    [onSearch]
  );

  return (
    <input
      type="search"
      onChange={e => debouncedSearch(e.target.value)}
    />
  );
}

function ScrollHandler({ onScroll }) {
  const throttledScroll = useMemo(
    () => throttle(onScroll, 100),
    [onScroll]
  );

  useEffect(() => {
    window.addEventListener('scroll', throttledScroll);
    return () => window.removeEventListener('scroll', throttledScroll);
  }, [throttledScroll]);
}
```

### Yield to Main Thread

```jsx
// For heavy operations in handlers
async function handleHeavyOperation() {
  // Process in chunks, yielding between
  for (let i = 0; i < items.length; i += 100) {
    processChunk(items.slice(i, i + 100));
    // Yield to allow paint/input
    await new Promise(resolve => setTimeout(resolve, 0));
  }
}
```

## List Virtualization

### Use Virtual Lists for Large Data

```jsx
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  return (
    <FixedSizeList
      height={600}
      width="100%"
      itemCount={items.length}
      itemSize={50}
    >
      {({ index, style }) => (
        <div style={style}>
          {items[index].name}
        </div>
      )}
    </FixedSizeList>
  );
}
```

### Windowing Benefits
- Only renders visible items
- Constant memory regardless of list size
- Smooth scrolling for 10K+ items

## State Management

### Colocate State

```jsx
// Bad: State too high in tree
function App() {
  const [inputValue, setInputValue] = useState(''); // Used only in SearchBox
  return (
    <Layout>
      <SearchBox value={inputValue} onChange={setInputValue} />
      <Content /> {/* Re-renders on every keystroke */}
    </Layout>
  );
}

// Good: State where it's used
function App() {
  return (
    <Layout>
      <SearchBox /> {/* Manages own state */}
      <Content /> {/* No unnecessary re-renders */}
    </Layout>
  );
}
```

### Split Context by Update Frequency

```jsx
// Bad: Single context, everything updates together
const AppContext = createContext({ user: null, theme: 'light', notifications: [] });

// Good: Split by update frequency
const UserContext = createContext(null);      // Rarely updates
const ThemeContext = createContext('light');  // Rarely updates
const NotificationContext = createContext([]); // Frequently updates
```

## Image Handling

### Lazy Load Images

```jsx
function LazyImage({ src, alt, ...props }) {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      {...props}
    />
  );
}
```

### Prevent CLS with Aspect Ratio

```jsx
function ResponsiveImage({ src, alt, aspectRatio = '16/9' }) {
  return (
    <div style={{ aspectRatio, position: 'relative' }}>
      <img
        src={src}
        alt={alt}
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
        loading="lazy"
      />
    </div>
  );
}
```

## Bundle Optimization

### Tree Shaking Imports

```jsx
// Bad: Imports entire library
import * as _ from 'lodash';
_.debounce(fn, 300);

// Good: Named imports (tree-shakeable)
import { debounce } from 'lodash-es';
debounce(fn, 300);

// Better: Direct path import
import debounce from 'lodash/debounce';
```

### Analyze Bundle Size

```bash
# With webpack
npx webpack-bundle-analyzer stats.json

# With Vite
npx vite-bundle-visualizer
```

### Common Bundle Bloat Sources

| Library | Size | Alternative |
|---------|------|-------------|
| moment | ~300KB | date-fns (~30KB) or Intl API |
| lodash | ~70KB | lodash-es + tree shaking |
| Material UI | varies | Import components directly |
| Chart.js | ~200KB | Lazy load, or lighter alternatives |

## Performance Debugging

### React DevTools Profiler
1. Open React DevTools → Profiler
2. Record interactions
3. Look for:
   - Components rendering unnecessarily
   - Long render times (> 16ms)
   - Cascading re-renders

### Why Did You Render

```jsx
// Development only
import whyDidYouRender from '@welldone-software/why-did-you-render';

whyDidYouRender(React, {
  trackAllPureComponents: true,
});

// Mark specific components
MyComponent.whyDidYouRender = true;
```

## Performance Checklist

### Initial Load
- [ ] Route-level code splitting
- [ ] Heavy components lazy loaded
- [ ] No barrel file imports (`import * from`)

### Runtime
- [ ] Large lists virtualized
- [ ] Event handlers debounced/throttled
- [ ] State colocated appropriately

### Re-renders
- [ ] memo() on expensive components
- [ ] useCallback for handler props
- [ ] useMemo for expensive calculations
- [ ] No inline objects in JSX

### Images
- [ ] loading="lazy" on below-fold images
- [ ] Explicit width/height or aspect-ratio
- [ ] Modern formats (WebP/AVIF)
