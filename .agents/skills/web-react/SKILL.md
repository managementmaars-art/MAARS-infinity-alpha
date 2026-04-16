---
name: web-react
cluster: web-dev
description: "React 19: hooks, context, suspense, server/client components, useActionState, compiler, React Query"
tags: ["react","components","hooks","web"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "react hooks components state suspense server client useActionState"
---

# web-react

## Purpose
This skill provides expertise in React 19 for building dynamic web applications, focusing on advanced features like hooks, context, suspense, server/client components, useActionState, the compiler, and React Query for efficient state management and data handling.

## When to Use
- Use for new React projects requiring modern hooks (e.g., useActionState) or server-side rendering with suspense.
- Apply when integrating data fetching with React Query in web apps, especially for real-time updates or API interactions.
- Choose for optimizing performance with server/client components in large-scale applications.
- Employ in scenarios needing context for global state without Redux, or when handling asynchronous operations with suspense.

## Key Capabilities
- Hooks: Use useState, useEffect, useContext for local state and side effects; useActionState for form state and actions in React 19.
- Context: Create context providers to share data across components, e.g., for theme or user auth.
- Suspense: Wrap components for lazy loading, like <Suspense fallback={<div>Loading...</div>}> for handling promises.
- Server/Client Components: Differentiate with 'use server' directive for server-only code and client components for interactivity.
- React Query: Manage server state with useQuery for fetching data, and useMutation for updates, caching responses automatically.
- Compiler: Leverage React 19's compiler for automatic optimizations, like bundling and tree-shaking in build tools.
- Additional: Handle forms with useActionState for server actions, reducing client-side JavaScript.

## Usage Patterns
- To manage state with hooks, import and use as follows:  
  ```jsx
  import { useState } from 'react';
  const [count, setCount] = useState(0);
  ```
- For context, create and consume it like this:  
  ```jsx
  import { createContext, useContext } from 'react';
  const ThemeContext = createContext('light');
  const App = () => useContext(ThemeContext);
  ```
- Implement suspense for lazy-loaded components:  
  ```jsx
  import { Suspense } from 'react';
  <Suspense fallback={<Spinner />}>
    <LazyComponent />
  </Suspense>
  ```
- Use React Query for data fetching:  
  ```jsx
  import { useQuery } from '@tanstack/react-query';
  const { data, isLoading } = useQuery(['key'], () => fetchData());
  ```
- For server/client components, mark files with 'use server' at the top for server-only logic, then import into client components.

## Common Commands/API
- Hooks API: Call useActionState for forms – e.g., const [state, action] = useActionState(formAction, initialState); where formAction is an async function.
- Suspense API: Use the suspense boundary as <React.Suspense> with a fallback prop for loading states.
- React Query commands: Run queries with useQuery hook; for mutations, use useMutation({ mutationFn: asyncFn }); CLI for React Query: npx @tanstack/query start for dev server.
- Compiler flags: In React 19 projects, use the compiler via build tools like Vite with flag --react-compiler to enable optimizations; in Webpack, add module: { rules: [{ test: /\.js$/, use: 'react-compiler' }] }.
- API endpoints: For React Query, fetch from endpoints like fetch('/api/data', { headers: { Authorization: `Bearer ${process.env.REACT_APP_API_KEY}` } }); set env var as $REACT_APP_API_KEY in .env files.
- Config formats: React Query config in code: const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 5 * 60 * 1000 } } }); for global settings.

## Integration Notes
- Integrate with other tools by installing dependencies: npm install react react-dom @tanstack/react-query; then wrap your app with <QueryClientProvider client={queryClient}>.
- For auth, use environment variables: Set $REACT_APP_API_KEY in your .env file and access via process.env.REACT_APP_API_KEY in fetch calls.
- When combining with server components, ensure server setup (e.g., Next.js) and use 'use server' directive; for client-side, import hooks directly.
- Link with web-dev cluster tools: If using a backend, configure React Query to handle CORS by setting proxy in package.json: "proxy": "http://localhost:5000".
- For React 19 features, ensure project uses React 19+; add to package.json: "react": "^19.0.0", and run npm install.

## Error Handling
- For hooks, catch errors in useEffect cleanups: useEffect(() => { const cleanup = () => { try { /* code */ } catch (e) { console.error(e); } }; return cleanup; }, []);
- Handle suspense errors with error boundaries: Create a component like class ErrorBoundary extends React.Component { state = { error: null }; componentDidCatch(error) { this.setState({ error }); } render() { return this.state.error ? <div>Error: {this.state.error.message}</div> : this.props.children; } }; Wrap suspense with it.
- In React Query, use onError in useQuery: useQuery({ queryFn: fetchData, onError: (error) => console.error('Fetch failed:', error) }); for global, set in QueryClient: new QueryClient({ defaultOptions: { queries: { onError: handleGlobalError } } }).
- For server components, handle fetch errors by checking responses: async function serverAction() { try { const res = await fetch('/api/data'); if (!res.ok) throw new Error('Network response not ok'); } catch (e) { return { error: e.message }; } }.
- Always use try-catch in async hooks like useActionState to prevent unhandled promises.

## Graph Relationships
- Related to cluster: web-dev (shares tools for web development).
- Connected to tags: react (core framework), hooks (specific APIs like useState), components (server/client types), web (overall domain).
- Links to other skills: Possibly integrates with "web-node" for backend API handling, or "data-fetching" for advanced querying.
