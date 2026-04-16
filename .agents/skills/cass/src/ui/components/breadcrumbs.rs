//! Breadcrumb bar component for the TUI.
//! Displays current context (Agent > Workspace > Date) and ranking.
//!
//! Legacy ratatui rendering has been removed.
//! The ftui equivalent lives in `src/ui/app.rs`.

use crate::ui::data::RankingMode;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BreadcrumbKind {
    Agent,
    Workspace,
    Date,
    Ranking,
    None,
}

pub fn ranking_label(r: RankingMode) -> &'static str {
    match r {
        RankingMode::RecentHeavy => "Recent",
        RankingMode::Balanced => "Balanced",
        RankingMode::RelevanceHeavy => "Relevance",
        RankingMode::MatchQualityHeavy => "Quality",
        RankingMode::DateNewest => "Newest",
        RankingMode::DateOldest => "Oldest",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_breadcrumb_kind_equality() {
        assert_eq!(BreadcrumbKind::Agent, BreadcrumbKind::Agent);
        assert_eq!(BreadcrumbKind::Workspace, BreadcrumbKind::Workspace);
        assert_eq!(BreadcrumbKind::Date, BreadcrumbKind::Date);
        assert_eq!(BreadcrumbKind::Ranking, BreadcrumbKind::Ranking);
        assert_eq!(BreadcrumbKind::None, BreadcrumbKind::None);
    }

    #[test]
    fn test_breadcrumb_kind_inequality() {
        assert_ne!(BreadcrumbKind::Agent, BreadcrumbKind::Workspace);
        assert_ne!(BreadcrumbKind::Date, BreadcrumbKind::Ranking);
        assert_ne!(BreadcrumbKind::None, BreadcrumbKind::Agent);
    }

    #[test]
    fn test_breadcrumb_kind_clone() {
        let kind = BreadcrumbKind::Agent;
        let cloned = kind;
        assert_eq!(kind, cloned);
    }

    #[test]
    fn test_breadcrumb_kind_copy() {
        let kind = BreadcrumbKind::Workspace;
        let copied: BreadcrumbKind = kind;
        assert_eq!(copied, BreadcrumbKind::Workspace);
    }

    #[test]
    fn test_breadcrumb_kind_debug() {
        let debug_str = format!("{:?}", BreadcrumbKind::Agent);
        assert!(debug_str.contains("Agent"));

        let debug_str = format!("{:?}", BreadcrumbKind::None);
        assert!(debug_str.contains("None"));
    }

    #[test]
    fn test_ranking_label_recent_heavy() {
        assert_eq!(ranking_label(RankingMode::RecentHeavy), "Recent");
    }

    #[test]
    fn test_ranking_label_balanced() {
        assert_eq!(ranking_label(RankingMode::Balanced), "Balanced");
    }

    #[test]
    fn test_ranking_label_relevance_heavy() {
        assert_eq!(ranking_label(RankingMode::RelevanceHeavy), "Relevance");
    }

    #[test]
    fn test_ranking_label_match_quality_heavy() {
        assert_eq!(ranking_label(RankingMode::MatchQualityHeavy), "Quality");
    }

    #[test]
    fn test_ranking_label_date_newest() {
        assert_eq!(ranking_label(RankingMode::DateNewest), "Newest");
    }

    #[test]
    fn test_ranking_label_date_oldest() {
        assert_eq!(ranking_label(RankingMode::DateOldest), "Oldest");
    }

    #[test]
    fn test_ranking_label_all_modes_non_empty() {
        let modes = [
            RankingMode::RecentHeavy,
            RankingMode::Balanced,
            RankingMode::RelevanceHeavy,
            RankingMode::MatchQualityHeavy,
            RankingMode::DateNewest,
            RankingMode::DateOldest,
        ];

        for mode in modes {
            let label = ranking_label(mode);
            assert!(
                !label.is_empty(),
                "Label for {:?} should not be empty",
                mode
            );
        }
    }
}
