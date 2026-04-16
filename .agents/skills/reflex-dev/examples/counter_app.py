"""
Simple Counter App - Demonstrates basic Reflex concepts

Shows: State management, event handlers, components, and styling
"""

import reflex as rx


class CounterState(rx.State):
    """State for the counter application."""

    count: int = 0
    step: int = 1

    def increment(self):
        """Increment counter by step value."""
        self.count += self.step

    def decrement(self):
        """Decrement counter by step value."""
        self.count -= self.step

    def reset(self):
        """Reset counter to zero."""
        self.count = 0

    def set_step(self, value: str):
        """Update the step value from input."""
        try:
            self.step = int(value) if value else 1
        except ValueError:
            self.step = 1


def index() -> rx.Component:
    """Main page of the counter app."""
    return rx.container(
        rx.vstack(
            rx.heading("Counter App", size="2xl", mb="4"),

            # Display current count
            rx.box(
                rx.text(
                    CounterState.count,
                    font_size="6xl",
                    font_weight="bold",
                    color="blue.600",
                ),
                bg="gray.100",
                padding="8",
                border_radius="lg",
                text_align="center",
                mb="6",
            ),

            # Control buttons
            rx.hstack(
                rx.button(
                    "- Decrement",
                    on_click=CounterState.decrement,
                    color_scheme="red",
                    size="lg",
                ),
                rx.button(
                    "Reset",
                    on_click=CounterState.reset,
                    color_scheme="gray",
                    size="lg",
                ),
                rx.button(
                    "+ Increment",
                    on_click=CounterState.increment,
                    color_scheme="green",
                    size="lg",
                ),
                spacing="4",
                mb="6",
            ),

            # Step size control
            rx.box(
                rx.text("Step Size:", font_weight="bold", mb="2"),
                rx.hstack(
                    rx.input(
                        value=CounterState.step.to_string(),
                        on_change=CounterState.set_step,
                        type="number",
                        width="100px",
                    ),
                    rx.text(f"(counting by {CounterState.step})"),
                    spacing="2",
                ),
                padding="4",
                border="1px solid #e2e8f0",
                border_radius="md",
            ),

            spacing="6",
            align="center",
            padding_y="20",
        ),
        max_width="600px",
        center_content=True,
    )


# Create and configure the app
app = rx.App()
app.add_page(index)
