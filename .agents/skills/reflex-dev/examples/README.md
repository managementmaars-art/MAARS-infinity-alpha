# Reflex Examples

Complete, working Reflex applications demonstrating common patterns and features.

## Running Examples

Each example is a standalone Reflex app. To run:

1. Install Reflex:
   ```bash
   pip install reflex
   ```

2. Navigate to this directory and copy the example:
   ```bash
   cp counter_app.py my_app.py
   ```

3. Initialize and run:
   ```bash
   reflex init
   reflex run
   ```

4. Open browser to `http://localhost:3000`

## Available Examples

### 1. Counter App (`counter_app.py`)

**Demonstrates:**
- Basic state management
- Event handlers
- Component composition
- Inline styling

**Features:**
- Increment/decrement counter
- Configurable step size
- Reset functionality

**Best For:** Learning Reflex basics, understanding state and event handlers

---

### 2. Data Table with CRUD (`data_table_crud.py`)

**Demonstrates:**
- List state management
- CRUD operations (Create, Read, Update, Delete)
- Forms with conditional rendering
- Data tables
- Computed vars

**Features:**
- View user data in table
- Add new users
- Edit existing users
- Delete users
- Form validation

**Best For:** Building admin panels, data management interfaces

---

### 3. Form with Validation (`form_validation.py`)

**Demonstrates:**
- Complex form handling
- Real-time validation
- Error messages
- Conditional rendering
- Component reusability

**Features:**
- Username validation (length, characters)
- Email validation (format)
- Password validation (strength requirements)
- Password confirmation matching
- Terms agreement checkbox
- Success/error states

**Best For:** User registration, complex forms, input validation

---

### 4. File Upload (`file_upload.py`)

**Demonstrates:**
- File upload handling
- Async operations
- Progress feedback
- File type validation
- File management

**Features:**
- Multi-file upload
- File type restrictions
- Upload progress
- File list with metadata
- File deletion
- Size calculations

**Best For:** Document management, media uploads, data import

## Customization Tips

### Styling
All examples use inline styling. You can customize colors, spacing, and layout by modifying style props:
```python
rx.box(
    bg="#your-color",
    padding="4",
    border_radius="md",
)
```

### State Extension
Add more state variables and event handlers to extend functionality:
```python
class MyState(rx.State):
    new_feature: str = ""

    def new_handler(self):
        # Your logic
        pass
```

### Component Reuse
Extract common patterns into reusable functions:
```python
def custom_button(text: str, handler) -> rx.Component:
    return rx.button(
        text,
        on_click=handler,
        color_scheme="blue",
        size="lg",
    )
```

## Integration with Existing Projects

These examples can be integrated into the Monaco Payroll System:

1. **Data Table CRUD** - Adapt for employee management, payroll record editing
2. **Form Validation** - Use for employee data entry, validation rules
3. **File Upload** - Integrate with Excel import/export functionality
4. **Counter App** - Adapt for statistics, counters in dashboard

## Additional Resources

- Reflex Documentation: https://reflex.dev/docs
- Component Library: https://reflex.dev/docs/library
- Community Examples: https://github.com/reflex-dev/reflex-examples
- Monaco Payroll Integration: See `references/patterns.md` for DuckDB/Polars patterns
