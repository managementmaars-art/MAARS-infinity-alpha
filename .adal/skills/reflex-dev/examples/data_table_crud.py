"""
Data Table with CRUD Operations

Demonstrates: Data tables, forms, CRUD operations, state management with lists
"""

import reflex as rx
from datetime import datetime


class DataTableState(rx.State):
    """State for managing a data table with CRUD operations."""

    # Data storage
    items: list[dict[str, str]] = [
        {"id": "1", "name": "Alice Smith", "email": "alice@example.com", "role": "Admin"},
        {"id": "2", "name": "Bob Jones", "email": "bob@example.com", "role": "User"},
        {"id": "3", "name": "Carol White", "email": "carol@example.com", "role": "User"},
    ]

    # Form fields
    form_id: str = ""
    form_name: str = ""
    form_email: str = ""
    form_role: str = "User"

    # UI state
    editing_id: str = ""
    show_form: bool = False

    @rx.var
    def next_id(self) -> str:
        """Generate next available ID."""
        if not self.items:
            return "1"
        max_id = max(int(item["id"]) for item in self.items)
        return str(max_id + 1)

    def toggle_form(self):
        """Show/hide the form."""
        self.show_form = not self.show_form
        if not self.show_form:
            self.clear_form()

    def clear_form(self):
        """Reset all form fields."""
        self.form_id = ""
        self.form_name = ""
        self.form_email = ""
        self.form_role = "User"
        self.editing_id = ""

    def add_item(self):
        """Add a new item to the table."""
        if self.form_name and self.form_email:
            new_item = {
                "id": self.next_id,
                "name": self.form_name,
                "email": self.form_email,
                "role": self.form_role,
            }
            self.items.append(new_item)
            self.clear_form()
            self.show_form = False

    def edit_item(self, item_id: str):
        """Load item data into form for editing."""
        for item in self.items:
            if item["id"] == item_id:
                self.form_name = item["name"]
                self.form_email = item["email"]
                self.form_role = item["role"]
                self.editing_id = item_id
                self.show_form = True
                break

    def update_item(self):
        """Update an existing item."""
        for i, item in enumerate(self.items):
            if item["id"] == self.editing_id:
                self.items[i] = {
                    "id": self.editing_id,
                    "name": self.form_name,
                    "email": self.form_email,
                    "role": self.form_role,
                }
                break
        self.clear_form()
        self.show_form = False

    def delete_item(self, item_id: str):
        """Delete an item from the table."""
        self.items = [item for item in self.items if item["id"] != item_id]


def item_form() -> rx.Component:
    """Form for adding/editing items."""
    return rx.box(
        rx.vstack(
            rx.heading(
                rx.cond(
                    DataTableState.editing_id != "",
                    "Edit Item",
                    "Add New Item"
                ),
                size="lg",
                mb="4",
            ),

            rx.input(
                placeholder="Name",
                value=DataTableState.form_name,
                on_change=DataTableState.set_form_name,
                width="100%",
            ),

            rx.input(
                placeholder="Email",
                value=DataTableState.form_email,
                on_change=DataTableState.set_form_email,
                type="email",
                width="100%",
            ),

            rx.select(
                ["Admin", "User", "Guest"],
                value=DataTableState.form_role,
                on_change=DataTableState.set_form_role,
                width="100%",
            ),

            rx.hstack(
                rx.button(
                    "Cancel",
                    on_click=DataTableState.toggle_form,
                    color_scheme="gray",
                ),
                rx.button(
                    rx.cond(
                        DataTableState.editing_id != "",
                        "Update",
                        "Add"
                    ),
                    on_click=rx.cond(
                        DataTableState.editing_id != "",
                        DataTableState.update_item,
                        DataTableState.add_item,
                    ),
                    color_scheme="blue",
                ),
                spacing="2",
                width="100%",
                justify="end",
            ),

            spacing="4",
            width="100%",
        ),
        bg="white",
        padding="6",
        border_radius="md",
        border="1px solid #e2e8f0",
        mb="6",
    )


def data_row(item: dict) -> rx.Component:
    """Render a single data row."""
    return rx.tr(
        rx.td(item["name"]),
        rx.td(item["email"]),
        rx.td(item["role"]),
        rx.td(
            rx.hstack(
                rx.button(
                    "Edit",
                    on_click=lambda: DataTableState.edit_item(item["id"]),
                    size="sm",
                    color_scheme="blue",
                ),
                rx.button(
                    "Delete",
                    on_click=lambda: DataTableState.delete_item(item["id"]),
                    size="sm",
                    color_scheme="red",
                ),
                spacing="2",
            )
        ),
    )


def index() -> rx.Component:
    """Main page with data table."""
    return rx.container(
        rx.vstack(
            rx.heading("User Management", size="2xl", mb="6"),

            # Add button
            rx.button(
                "+ Add New User",
                on_click=DataTableState.toggle_form,
                color_scheme="green",
                mb="4",
            ),

            # Form (conditional)
            rx.cond(
                DataTableState.show_form,
                item_form(),
                rx.box(),
            ),

            # Data table
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Email"),
                        rx.table.column_header_cell("Role"),
                        rx.table.column_header_cell("Actions"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(DataTableState.items, data_row),
                ),
                variant="surface",
                width="100%",
            ),

            spacing="4",
            width="100%",
            padding_y="8",
        ),
        max_width="900px",
    )


app = rx.App()
app.add_page(index)
