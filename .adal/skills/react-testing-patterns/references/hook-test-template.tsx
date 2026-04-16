/**
 * Hook Test Template
 *
 * Patterns for testing custom React hooks with renderHook.
 */
import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useCounter } from "./useCounter";
import { useUsers } from "./useUsers";

// ---------- Simple Synchronous Hook ----------

describe("useCounter", () => {
  it("starts with initial value", () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });

  it("increments the count", () => {
    const { result } = renderHook(() => useCounter(0));

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it("decrements the count", () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });

  it("resets to initial value", () => {
    const { result } = renderHook(() => useCounter(0));

    act(() => {
      result.current.increment();
      result.current.increment();
      result.current.reset();
    });

    expect(result.current.count).toBe(0);
  });
});

// ---------- Hook with Changing Props ----------

describe("useDebounce", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns initial value immediately", () => {
    const { result } = renderHook(() => useDebounce("hello", 300));
    expect(result.current).toBe("hello");
  });

  it("updates value after delay", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: "hello" } },
    );

    // Change the value
    rerender({ value: "world" });

    // Not yet updated
    expect(result.current).toBe("hello");

    // Advance timers past the delay
    act(() => {
      vi.advanceTimersByTime(300);
    });

    // Now updated
    expect(result.current).toBe("world");
  });
});

// ---------- Async Hook with TanStack Query ----------

// Helper: create a fresh QueryClient wrapper for each test
function createTestWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe("useUsers (TanStack Query hook)", () => {
  it("starts in pending state", () => {
    const { result } = renderHook(() => useUsers(), {
      wrapper: createTestWrapper(),
    });

    expect(result.current.isPending).toBe(true);
    expect(result.current.data).toBeUndefined();
  });

  it("returns user data on success", async () => {
    const { result } = renderHook(() => useUsers(), {
      wrapper: createTestWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data![0].displayName).toBe("Alice");
  });

  it("returns error on failure", async () => {
    // Override MSW handler for this test
    server.use(
      http.get("/api/users", () => {
        return HttpResponse.json(
          { detail: "Server error", code: "INTERNAL_ERROR" },
          { status: 500 },
        );
      }),
    );

    const { result } = renderHook(() => useUsers(), {
      wrapper: createTestWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

// ---------- Hook with Side Effects ----------

describe("useLocalStorage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("returns initial value when no stored value exists", () => {
    const { result } = renderHook(() =>
      useLocalStorage("theme", "light"),
    );
    expect(result.current[0]).toBe("light");
  });

  it("returns stored value when it exists", () => {
    localStorage.setItem("theme", JSON.stringify("dark"));

    const { result } = renderHook(() =>
      useLocalStorage("theme", "light"),
    );
    expect(result.current[0]).toBe("dark");
  });

  it("updates localStorage when value changes", () => {
    const { result } = renderHook(() =>
      useLocalStorage("theme", "light"),
    );

    act(() => {
      result.current[1]("dark");
    });

    expect(result.current[0]).toBe("dark");
    expect(JSON.parse(localStorage.getItem("theme")!)).toBe("dark");
  });
});
