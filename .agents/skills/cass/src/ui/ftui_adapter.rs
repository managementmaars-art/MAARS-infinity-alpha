//! Thin FrankenTUI adapter for cass UI migration.
//!
//! Centralizes high-frequency imports so the migration can switch internals
//! without touching every call site repeatedly.

pub use ftui::core::geometry::{Rect, Sides, Size};
pub use ftui::layout::{Alignment, Constraint, Direction, Flex, Grid, LayoutSizeHint};
pub use ftui::render::budget::{DegradationLevel, FrameBudgetConfig};
pub use ftui::widgets::{StatefulWidget, Widget};
pub use ftui::{
    App, Cmd, Event, Frame, KeyCode, KeyEvent, Model, Modifiers, Program, RuntimeDiffConfig,
    ScreenMode, Style, TerminalWriter, Theme, UiAnchor,
};

// ---------------------------------------------------------------------------
// Animation primitives (ftui-core)
// ---------------------------------------------------------------------------
pub use ftui::core::animation::presets as anim_presets;
pub use ftui::core::animation::{
    Animation, AnimationGroup, Callbacks, Spring, StaggerMode, Timeline, stagger_offsets,
};
