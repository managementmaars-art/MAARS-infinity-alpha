/**
 * Component Test Template
 *
 * Copy this template as a starting point for component tests.
 * Adapt the imports, props, and assertions to your component.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe, toHaveNoViolations } from "jest-axe";
import { ExampleComponent } from "./ExampleComponent";

// Extend expect with accessibility matchers
expect.extend(toHaveNoViolations);

// Default props — reuse across tests, override per-test as needed
const defaultProps = {
  title: "Test Title",
  onAction: vi.fn(),
  items: [
    { id: 1, name: "Item 1" },
    { id: 2, name: "Item 2" },
  ],
};

describe("ExampleComponent", () => {
  // Reset mocks between tests
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---------- Rendering ----------

  it("renders the title", () => {
    render(<ExampleComponent {...defaultProps} />);
    expect(screen.getByRole("heading", { name: "Test Title" })).toBeInTheDocument();
  });

  it("renders all items", () => {
    render(<ExampleComponent {...defaultProps} />);
    expect(screen.getAllByRole("listitem")).toHaveLength(2);
  });

  it("renders empty state when no items", () => {
    render(<ExampleComponent {...defaultProps} items={[]} />);
    expect(screen.getByText(/no items/i)).toBeInTheDocument();
  });

  // ---------- User Interaction ----------

  it("calls onAction when action button is clicked", async () => {
    const user = userEvent.setup();
    render(<ExampleComponent {...defaultProps} />);

    await user.click(screen.getByRole("button", { name: /action/i }));

    expect(defaultProps.onAction).toHaveBeenCalledTimes(1);
  });

  it("filters items when search is typed", async () => {
    const user = userEvent.setup();
    render(<ExampleComponent {...defaultProps} />);

    await user.type(screen.getByRole("searchbox"), "Item 1");

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.queryByText("Item 2")).not.toBeInTheDocument();
  });

  // ---------- Async Behavior ----------

  it("shows loading state while fetching", () => {
    render(<ExampleComponent {...defaultProps} isLoading />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows data after loading completes", async () => {
    render(<ExampleComponent {...defaultProps} />);

    // Use findBy for elements that appear asynchronously
    const heading = await screen.findByRole("heading", { name: "Test Title" });
    expect(heading).toBeInTheDocument();
  });

  // ---------- Accessibility ----------

  it("has no accessibility violations", async () => {
    const { container } = render(<ExampleComponent {...defaultProps} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("has no accessibility violations in empty state", async () => {
    const { container } = render(<ExampleComponent {...defaultProps} items={[]} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
