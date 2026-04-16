"""
Form with Validation - Demonstrates form handling and validation

Shows: Form inputs, validation logic, error messages, conditional rendering
"""

import reflex as rx
import re


class FormState(rx.State):
    """State for form with validation."""

    # Form fields
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    agree_terms: bool = False

    # Validation errors
    username_error: str = ""
    email_error: str = ""
    password_error: str = ""
    confirm_password_error: str = ""

    # Submission state
    submitted: bool = False

    def validate_username(self):
        """Validate username field."""
        if len(self.username) < 3:
            self.username_error = "Username must be at least 3 characters"
        elif len(self.username) > 20:
            self.username_error = "Username must be less than 20 characters"
        elif not re.match("^[a-zA-Z0-9_]+$", self.username):
            self.username_error = "Username can only contain letters, numbers, and underscores"
        else:
            self.username_error = ""

    def validate_email(self):
        """Validate email field."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not self.email:
            self.email_error = "Email is required"
        elif not re.match(email_pattern, self.email):
            self.email_error = "Please enter a valid email address"
        else:
            self.email_error = ""

    def validate_password(self):
        """Validate password field."""
        if len(self.password) < 8:
            self.password_error = "Password must be at least 8 characters"
        elif not re.search(r"[A-Z]", self.password):
            self.password_error = "Password must contain at least one uppercase letter"
        elif not re.search(r"[a-z]", self.password):
            self.password_error = "Password must contain at least one lowercase letter"
        elif not re.search(r"[0-9]", self.password):
            self.password_error = "Password must contain at least one number"
        else:
            self.password_error = ""

    def validate_confirm_password(self):
        """Validate password confirmation."""
        if self.confirm_password != self.password:
            self.confirm_password_error = "Passwords do not match"
        else:
            self.confirm_password_error = ""

    @rx.var
    def is_valid(self) -> bool:
        """Check if form is valid."""
        return (
            self.username != "" and
            self.email != "" and
            self.password != "" and
            self.confirm_password != "" and
            self.agree_terms and
            self.username_error == "" and
            self.email_error == "" and
            self.password_error == "" and
            self.confirm_password_error == ""
        )

    def handle_submit(self):
        """Handle form submission."""
        # Run all validations
        self.validate_username()
        self.validate_email()
        self.validate_password()
        self.validate_confirm_password()

        # Submit if valid
        if self.is_valid:
            self.submitted = True
            # In real app: save to database, send to API, etc.

    def reset_form(self):
        """Reset form to initial state."""
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.agree_terms = False
        self.username_error = ""
        self.email_error = ""
        self.password_error = ""
        self.confirm_password_error = ""
        self.submitted = False


def form_field(
    label: str,
    value: str,
    on_change,
    on_blur,
    error: str,
    field_type: str = "text",
    placeholder: str = "",
) -> rx.Component:
    """Reusable form field with validation."""
    return rx.vstack(
        rx.text(label, font_weight="bold", mb="1"),
        rx.input(
            value=value,
            on_change=on_change,
            on_blur=on_blur,
            type=field_type,
            placeholder=placeholder,
            width="100%",
            border_color=rx.cond(error != "", "red.500", "gray.300"),
        ),
        rx.cond(
            error != "",
            rx.text(error, color="red.500", font_size="sm"),
            rx.box(),
        ),
        align="start",
        width="100%",
        spacing="1",
    )


def registration_form() -> rx.Component:
    """Registration form with validation."""
    return rx.box(
        rx.vstack(
            rx.heading("Create Account", size="2xl", mb="6"),

            # Username field
            form_field(
                label="Username",
                value=FormState.username,
                on_change=FormState.set_username,
                on_blur=FormState.validate_username,
                error=FormState.username_error,
                placeholder="Choose a username",
            ),

            # Email field
            form_field(
                label="Email",
                value=FormState.email,
                on_change=FormState.set_email,
                on_blur=FormState.validate_email,
                error=FormState.email_error,
                field_type="email",
                placeholder="your.email@example.com",
            ),

            # Password field
            form_field(
                label="Password",
                value=FormState.password,
                on_change=FormState.set_password,
                on_blur=FormState.validate_password,
                error=FormState.password_error,
                field_type="password",
                placeholder="Min. 8 chars, 1 uppercase, 1 number",
            ),

            # Confirm password field
            form_field(
                label="Confirm Password",
                value=FormState.confirm_password,
                on_change=FormState.set_confirm_password,
                on_blur=FormState.validate_confirm_password,
                error=FormState.confirm_password_error,
                field_type="password",
                placeholder="Re-enter your password",
            ),

            # Terms checkbox
            rx.checkbox(
                "I agree to the terms and conditions",
                checked=FormState.agree_terms,
                on_change=FormState.set_agree_terms,
            ),

            # Submit button
            rx.button(
                "Create Account",
                on_click=FormState.handle_submit,
                color_scheme="blue",
                size="lg",
                width="100%",
                disabled=~FormState.is_valid,
            ),

            spacing="4",
            width="100%",
        ),
        max_width="500px",
        padding="8",
        bg="white",
        border_radius="lg",
        box_shadow="lg",
    )


def success_message() -> rx.Component:
    """Success message after submission."""
    return rx.box(
        rx.vstack(
            rx.icon("check_circle", size=64, color="green.500"),
            rx.heading("Account Created!", size="2xl", color="green.700"),
            rx.text(f"Welcome, {FormState.username}!", font_size="lg"),
            rx.text(f"Confirmation email sent to {FormState.email}", color="gray.600"),
            rx.button(
                "Create Another Account",
                on_click=FormState.reset_form,
                color_scheme="blue",
                mt="4",
            ),
            spacing="4",
            align="center",
        ),
        max_width="500px",
        padding="8",
        bg="white",
        border_radius="lg",
        box_shadow="lg",
        text_align="center",
    )


def index() -> rx.Component:
    """Main page."""
    return rx.container(
        rx.center(
            rx.cond(
                FormState.submitted,
                success_message(),
                registration_form(),
            ),
            min_height="100vh",
            padding_y="8",
        ),
        bg="gray.50",
    )


app = rx.App()
app.add_page(index)
