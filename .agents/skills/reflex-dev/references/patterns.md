# Common Reflex Patterns

This reference provides detailed examples of common patterns in Reflex applications.

## Authentication Flows

### Basic Authentication with Session State

```python
import reflex as rx
import bcrypt


class AuthState(rx.State):
    """Authentication state management."""

    username: str = ""
    is_authenticated: bool = False
    error_message: str = ""

    def login(self, form_data: dict):
        """Handle login with username/password."""
        username = form_data.get("username", "")
        password = form_data.get("password", "")

        # In production: check against database
        # For demo: simple hardcoded check
        if username == "admin" and password == "password":
            self.username = username
            self.is_authenticated = True
            return rx.redirect("/dashboard")
        else:
            self.error_message = "Invalid credentials"

    def logout(self):
        """Clear session and redirect to login."""
        self.username = ""
        self.is_authenticated = False
        return rx.redirect("/login")

    def check_auth(self):
        """Redirect to login if not authenticated."""
        if not self.is_authenticated:
            return rx.redirect("/login")


def login_page():
    return rx.container(
        rx.form(
            rx.vstack(
                rx.heading("Login"),
                rx.input(name="username", placeholder="Username"),
                rx.input(name="password", type="password", placeholder="Password"),
                rx.cond(
                    AuthState.error_message != "",
                    rx.text(AuthState.error_message, color="red"),
                    rx.box(),
                ),
                rx.button("Login", type="submit"),
            ),
            on_submit=AuthState.login,
        ),
    )


def protected_page():
    return rx.container(
        rx.vstack(
            rx.heading(f"Welcome, {AuthState.username}!"),
            rx.button("Logout", on_click=AuthState.logout),
        ),
        on_mount=AuthState.check_auth,
    )
```

### Protected Routes Pattern

```python
def require_auth(page_func):
    """Decorator to protect routes."""
    def wrapper():
        return rx.cond(
            AuthState.is_authenticated,
            page_func(),
            rx.redirect("/login"),
        )
    return wrapper


@require_auth
def admin_page():
    return rx.container(
        rx.heading("Admin Dashboard"),
        # Admin content
    )
```

## Real-Time Updates

### WebSocket State Updates

```python
import reflex as rx
import asyncio


class LiveDataState(rx.State):
    """Real-time data updates."""

    current_value: float = 0.0
    data_points: list[float] = []
    is_streaming: bool = False

    async def start_streaming(self):
        """Start streaming data updates."""
        self.is_streaming = True

        while self.is_streaming:
            # Simulate real-time data (replace with actual data source)
            import random
            self.current_value = random.uniform(0, 100)
            self.data_points.append(self.current_value)

            # Keep only last 50 points
            if len(self.data_points) > 50:
                self.data_points = self.data_points[-50:]

            # Update every second
            await asyncio.sleep(1)

    def stop_streaming(self):
        """Stop streaming."""
        self.is_streaming = False


def live_dashboard():
    return rx.vstack(
        rx.heading(f"Current Value: {LiveDataState.current_value:.2f}"),
        rx.recharts.line_chart(
            rx.recharts.line(data_key="value"),
            data=[{"value": v} for v in LiveDataState.data_points],
            width="100%",
            height=300,
        ),
        rx.button(
            "Start Streaming",
            on_click=LiveDataState.start_streaming,
            disabled=LiveDataState.is_streaming,
        ),
        rx.button(
            "Stop Streaming",
            on_click=LiveDataState.stop_streaming,
            disabled=~LiveDataState.is_streaming,
        ),
    )
```

### Auto-Refresh Pattern

```python
class RefreshState(rx.State):
    """Auto-refresh data at intervals."""

    data: list[dict] = []
    last_updated: str = ""

    async def auto_refresh(self):
        """Refresh data every N seconds."""
        while True:
            await self.load_data()
            await asyncio.sleep(30)  # Refresh every 30 seconds

    async def load_data(self):
        """Load data from source."""
        # Replace with actual data loading
        from datetime import datetime
        self.data = await fetch_from_api()
        self.last_updated = datetime.now().strftime("%H:%M:%S")


def auto_refresh_page():
    return rx.container(
        rx.vstack(
            rx.text(f"Last updated: {RefreshState.last_updated}"),
            # Display data
        ),
        on_mount=RefreshState.auto_refresh,
    )
```

## Complex Form Validation

### Multi-Step Form

```python
class MultiStepFormState(rx.State):
    """Multi-step form with validation."""

    # Current step
    current_step: int = 1

    # Step 1: Personal info
    first_name: str = ""
    last_name: str = ""
    email: str = ""

    # Step 2: Address
    street: str = ""
    city: str = ""
    zip_code: str = ""

    # Step 3: Preferences
    newsletter: bool = False
    notifications: bool = True

    @rx.var
    def step1_valid(self) -> bool:
        """Check if step 1 is complete."""
        return (
            len(self.first_name) > 0 and
            len(self.last_name) > 0 and
            "@" in self.email
        )

    @rx.var
    def step2_valid(self) -> bool:
        """Check if step 2 is complete."""
        return (
            len(self.street) > 0 and
            len(self.city) > 0 and
            len(self.zip_code) == 5
        )

    def next_step(self):
        """Advance to next step."""
        if self.current_step < 3:
            self.current_step += 1

    def prev_step(self):
        """Go back one step."""
        if self.current_step > 1:
            self.current_step -= 1

    def submit_form(self):
        """Submit complete form."""
        # Process form data
        print(f"Submitted: {self.first_name} {self.last_name}")
        # Reset form
        self.current_step = 1


def step1():
    return rx.vstack(
        rx.heading("Step 1: Personal Information"),
        rx.input(
            placeholder="First Name",
            value=MultiStepFormState.first_name,
            on_change=MultiStepFormState.set_first_name,
        ),
        rx.input(
            placeholder="Last Name",
            value=MultiStepFormState.last_name,
            on_change=MultiStepFormState.set_last_name,
        ),
        rx.input(
            placeholder="Email",
            type="email",
            value=MultiStepFormState.email,
            on_change=MultiStepFormState.set_email,
        ),
        rx.button(
            "Next",
            on_click=MultiStepFormState.next_step,
            disabled=~MultiStepFormState.step1_valid,
        ),
    )


def step2():
    return rx.vstack(
        rx.heading("Step 2: Address"),
        rx.input(
            placeholder="Street",
            value=MultiStepFormState.street,
            on_change=MultiStepFormState.set_street,
        ),
        rx.input(
            placeholder="City",
            value=MultiStepFormState.city,
            on_change=MultiStepFormState.set_city,
        ),
        rx.input(
            placeholder="ZIP Code",
            value=MultiStepFormState.zip_code,
            on_change=MultiStepFormState.set_zip_code,
        ),
        rx.hstack(
            rx.button("Back", on_click=MultiStepFormState.prev_step),
            rx.button(
                "Next",
                on_click=MultiStepFormState.next_step,
                disabled=~MultiStepFormState.step2_valid,
            ),
        ),
    )


def step3():
    return rx.vstack(
        rx.heading("Step 3: Preferences"),
        rx.checkbox(
            "Subscribe to newsletter",
            checked=MultiStepFormState.newsletter,
            on_change=MultiStepFormState.set_newsletter,
        ),
        rx.checkbox(
            "Enable notifications",
            checked=MultiStepFormState.notifications,
            on_change=MultiStepFormState.set_notifications,
        ),
        rx.hstack(
            rx.button("Back", on_click=MultiStepFormState.prev_step),
            rx.button("Submit", on_click=MultiStepFormState.submit_form),
        ),
    )


def multi_step_form():
    return rx.container(
        rx.cond(
            MultiStepFormState.current_step == 1,
            step1(),
            rx.cond(
                MultiStepFormState.current_step == 2,
                step2(),
                step3(),
            ),
        ),
    )
```

### Dependent Fields Pattern

```python
class DependentFieldsState(rx.State):
    """Form with dependent/conditional fields."""

    country: str = ""
    state: str = ""
    province: str = ""

    # Available states/provinces by country
    us_states: list[str] = ["California", "New York", "Texas"]
    canada_provinces: list[str] = ["Ontario", "Quebec", "British Columbia"]

    @rx.var
    def show_state_field(self) -> bool:
        """Show state field only for US."""
        return self.country == "United States"

    @rx.var
    def show_province_field(self) -> bool:
        """Show province field only for Canada."""
        return self.country == "Canada"

    @rx.var
    def region_options(self) -> list[str]:
        """Get appropriate region options."""
        if self.country == "United States":
            return self.us_states
        elif self.country == "Canada":
            return self.canada_provinces
        return []


def dependent_form():
    return rx.vstack(
        rx.select(
            ["United States", "Canada", "Other"],
            placeholder="Select Country",
            value=DependentFieldsState.country,
            on_change=DependentFieldsState.set_country,
        ),

        # Conditional US state field
        rx.cond(
            DependentFieldsState.show_state_field,
            rx.select(
                DependentFieldsState.us_states,
                placeholder="Select State",
                value=DependentFieldsState.state,
                on_change=DependentFieldsState.set_state,
            ),
            rx.box(),
        ),

        # Conditional Canada province field
        rx.cond(
            DependentFieldsState.show_province_field,
            rx.select(
                DependentFieldsState.canada_provinces,
                placeholder="Select Province",
                value=DependentFieldsState.province,
                on_change=DependentFieldsState.set_province,
            ),
            rx.box(),
        ),
    )
```

## Data Visualization with Charts

### Interactive Dashboard

```python
class DashboardState(rx.State):
    """Dashboard with multiple chart types."""

    sales_data: list[dict] = [
        {"month": "Jan", "sales": 4000, "profit": 2400},
        {"month": "Feb", "sales": 3000, "profit": 1398},
        {"month": "Mar", "sales": 2000, "profit": 9800},
        {"month": "Apr", "sales": 2780, "profit": 3908},
        {"month": "May", "sales": 1890, "profit": 4800},
        {"month": "Jun", "sales": 2390, "profit": 3800},
    ]

    category_data: list[dict] = [
        {"name": "Electronics", "value": 400},
        {"name": "Clothing", "value": 300},
        {"name": "Food", "value": 300},
        {"name": "Books", "value": 200},
    ]


def dashboard():
    return rx.container(
        rx.vstack(
            rx.heading("Sales Dashboard", size="2xl"),

            # Line chart
            rx.box(
                rx.heading("Monthly Sales & Profit", size="lg", mb="2"),
                rx.recharts.line_chart(
                    rx.recharts.line(data_key="sales", stroke="#8884d8"),
                    rx.recharts.line(data_key="profit", stroke="#82ca9d"),
                    rx.recharts.x_axis(data_key="month"),
                    rx.recharts.y_axis(),
                    rx.recharts.legend(),
                    data=DashboardState.sales_data,
                    width="100%",
                    height=300,
                ),
            ),

            # Bar chart
            rx.box(
                rx.heading("Category Distribution", size="lg", mb="2"),
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="value", fill="#8884d8"),
                    rx.recharts.x_axis(data_key="name"),
                    rx.recharts.y_axis(),
                    data=DashboardState.category_data,
                    width="100%",
                    height=300,
                ),
            ),

            # Pie chart
            rx.box(
                rx.heading("Market Share", size="lg", mb="2"),
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        data=DashboardState.category_data,
                        data_key="value",
                        name_key="name",
                        fill="#8884d8",
                    ),
                    rx.recharts.legend(),
                    width="100%",
                    height=300,
                ),
            ),

            spacing="8",
        ),
    )
```

## Database Patterns

### DuckDB Integration

```python
import duckdb
import polars as pl


class DBIntegrationState(rx.State):
    """DuckDB database integration."""

    records: list[dict] = []
    filtered_records: list[dict] = []
    search_term: str = ""

    async def load_all_records(self):
        """Load all records from database."""
        conn = duckdb.connect("data/app.duckdb")
        df = conn.execute("SELECT * FROM users").pl()
        self.records = df.to_dicts()
        conn.close()

    async def search_records(self):
        """Search records by term."""
        if not self.search_term:
            self.filtered_records = self.records
            return

        conn = duckdb.connect("data/app.duckdb")
        query = """
            SELECT * FROM users
            WHERE name LIKE ? OR email LIKE ?
        """
        search_pattern = f"%{self.search_term}%"
        df = conn.execute(query, [search_pattern, search_pattern]).pl()
        self.filtered_records = df.to_dicts()
        conn.close()

    async def add_record(self, data: dict):
        """Insert new record."""
        conn = duckdb.connect("data/app.duckdb")
        conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [data["name"], data["email"]]
        )
        conn.close()
        await self.load_all_records()

    async def delete_record(self, user_id: int):
        """Delete record by ID."""
        conn = duckdb.connect("data/app.duckdb")
        conn.execute("DELETE FROM users WHERE id = ?", [user_id])
        conn.close()
        await self.load_all_records()
```

### Polars Data Processing

```python
import polars as pl


class DataProcessingState(rx.State):
    """Polars data processing patterns."""

    raw_data: list[dict] = []
    processed_data: list[dict] = []

    async def process_data(self):
        """Process data using Polars."""
        # Convert to Polars DataFrame
        df = pl.DataFrame(self.raw_data)

        # Example processing pipeline
        processed = (
            df
            .filter(pl.col("amount") > 100)
            .group_by("category")
            .agg([
                pl.col("amount").sum().alias("total"),
                pl.col("amount").mean().alias("average"),
                pl.col("id").count().alias("count"),
            ])
            .sort("total", descending=True)
        )

        self.processed_data = processed.to_dicts()
```

## Advanced Component Patterns

### Reusable Data Card

```python
def data_card(
    title: str,
    value: str,
    change: str,
    icon: str,
    color: str = "blue",
) -> rx.Component:
    """Reusable card component for displaying metrics."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=32, color=f"{color}.500"),
                rx.spacer(),
                rx.badge(change, color_scheme="green" if "+" in change else "red"),
                width="100%",
            ),
            rx.text(title, font_size="sm", color="gray.600"),
            rx.heading(value, size="2xl", color=f"{color}.600"),
            spacing="2",
            align="start",
        ),
        padding="6",
        border_radius="lg",
        bg="white",
        box_shadow="md",
        width="100%",
    )


def metrics_dashboard():
    return rx.responsive_grid(
        data_card("Total Sales", "$45,231", "+12.5%", "trending_up", "blue"),
        data_card("New Users", "1,234", "+5.2%", "person_add", "green"),
        data_card("Revenue", "$12,345", "+8.1%", "attach_money", "purple"),
        data_card("Orders", "567", "-2.4%", "shopping_cart", "orange"),
        columns=[1, 2, 4],
        spacing="4",
    )
```

### Modal Dialog Pattern

```python
class ModalState(rx.State):
    """Modal dialog state."""

    show_modal: bool = False
    selected_item: dict = {}

    def open_modal(self, item: dict):
        """Open modal with item data."""
        self.selected_item = item
        self.show_modal = True

    def close_modal(self):
        """Close modal."""
        self.show_modal = False
        self.selected_item = {}


def modal_dialog():
    return rx.cond(
        ModalState.show_modal,
        rx.box(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Item Details"),
                        rx.spacer(),
                        rx.button("×", on_click=ModalState.close_modal),
                        width="100%",
                    ),
                    rx.text(f"Name: {ModalState.selected_item.get('name', '')}"),
                    rx.text(f"Value: {ModalState.selected_item.get('value', '')}"),
                    rx.button("Close", on_click=ModalState.close_modal),
                ),
                bg="white",
                padding="6",
                border_radius="lg",
                max_width="500px",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            bg="rgba(0,0,0,0.5)",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="1000",
        ),
        rx.box(),
    )
```

## Performance Optimization

### Lazy Loading Pattern

```python
class LazyLoadState(rx.State):
    """Lazy load data as user scrolls."""

    items: list[dict] = []
    page: int = 1
    has_more: bool = True
    is_loading: bool = False

    async def load_more(self):
        """Load next page of data."""
        if self.is_loading or not self.has_more:
            return

        self.is_loading = True

        # Fetch next page (replace with actual API call)
        new_items = await fetch_page(self.page)

        if new_items:
            self.items.extend(new_items)
            self.page += 1
        else:
            self.has_more = False

        self.is_loading = False


def lazy_list():
    return rx.vstack(
        rx.foreach(LazyLoadState.items, lambda item: rx.text(item["name"])),
        rx.cond(
            LazyLoadState.has_more,
            rx.button(
                "Load More",
                on_click=LazyLoadState.load_more,
                disabled=LazyLoadState.is_loading,
            ),
            rx.text("No more items"),
        ),
    )
```

### Debounced Search

```python
import asyncio


class SearchState(rx.State):
    """Debounced search implementation."""

    search_query: str = ""
    search_results: list[dict] = []
    is_searching: bool = False
    _search_task: asyncio.Task = None

    async def debounced_search(self, query: str):
        """Search with 500ms debounce."""
        self.search_query = query

        # Cancel previous search
        if self._search_task and not self._search_task.done():
            self._search_task.cancel()

        # Start new search after delay
        self._search_task = asyncio.create_task(self._perform_search())

    async def _perform_search(self):
        """Perform the actual search after delay."""
        await asyncio.sleep(0.5)  # 500ms debounce

        if not self.search_query:
            self.search_results = []
            return

        self.is_searching = True

        # Perform search (replace with actual search)
        results = await search_api(self.search_query)
        self.search_results = results

        self.is_searching = False


def search_box():
    return rx.vstack(
        rx.input(
            placeholder="Search...",
            value=SearchState.search_query,
            on_change=SearchState.debounced_search,
        ),
        rx.cond(
            SearchState.is_searching,
            rx.spinner(),
            rx.foreach(
                SearchState.search_results,
                lambda r: rx.text(r["title"]),
            ),
        ),
    )
```
