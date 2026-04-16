//! UI components registry plus retained legacy shell modules.
//!
//! [`help_strip`] and [`widgets`] are intentional comment-only legacy shells.
//! The active FTUI-era component state and rendering logic live in the
//! neighboring component modules and [`crate::ui::app`].
pub mod breadcrumbs;
pub mod export_modal;
/// Retained legacy shell module; active help-strip behavior lives elsewhere.
pub mod help_strip;
pub mod palette;
pub mod pills;
pub mod theme;
pub mod toast;
/// Retained legacy shell module; active widget behavior lives elsewhere.
pub mod widgets;

#[cfg(test)]
mod tests {
    use super::export_modal::ExportModalState;
    use super::palette::PaletteState;
    use super::toast::ToastManager;

    #[test]
    fn canonical_component_types_live_outside_legacy_shell_modules() {
        let _ = std::mem::size_of::<ExportModalState>();
        let _ = std::mem::size_of::<PaletteState>();
        let _ = std::mem::size_of::<ToastManager>();
    }
}
