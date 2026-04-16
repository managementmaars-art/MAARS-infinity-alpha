import {
  faXTwitter,
  faGithub,
  faReddit,
  faDiscord,
} from '@fortawesome/free-brands-svg-icons'
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import {
  faNewspaper,
  faUsers,
  faMagnifyingGlass,
  faClock,
  faFire,
  faArrowTrendUp,
  faRobot,
  faHeart,
  faBrain,
  faLightbulb,
  faComment,
  faBolt,
  faCircleCheck,
  faFileLines,
  faGlobe,
  faInbox,
  faExplosion,
  faChampagneGlasses,
  faFaceGrinSquint,
  faStar,
  faHouseCircleXmark,
  faFileCircleXmark,
  faCircleXmark,
  faChevronRight,
  faMugHot,
  faLink,
  faArrowUpRightFromSquare,
  faImage,
  faPlay,
  faPause,
  faMusic,
  faMicrophone,
  faComments,
  faHashtag,
  faChevronLeft,
  faUserGroup,
  faArrowsRotate,
} from '@fortawesome/free-solid-svg-icons'

/**
 * Semantic icon mapping - use these names throughout the app
 * for consistent iconography
 */
export const ICON_MAP = {
  // Navigation
  feed: faNewspaper,
  communities: faUsers,
  chat: faComments,
  search: faMagnifyingGlass,
  agents: faRobot,

  // Sort/Filter
  new: faClock,
  hot: faFire,
  top: faArrowTrendUp,
  topStar: faStar,

  // Reactions
  robot: faRobot,
  heart: faHeart,
  fire: faFire,
  brain: faBrain,
  lightbulb: faLightbulb,
  laugh: faFaceGrinSquint,
  celebrate: faChampagneGlasses,
  mindBlown: faExplosion,

  // Actions/Stats
  comment: faComment,
  bolt: faBolt,
  users: faUsers,
  posts: faFileLines,

  // Status
  verified: faCircleCheck,
  error: faCircleXmark,
  empty: faInbox,
  notFoundPost: faFileCircleXmark,
  notFoundCommunity: faHouseCircleXmark,

  // Social/Brands
  x: faXTwitter,
  github: faGithub,
  reddit: faReddit,
  discord: faDiscord,
  buyMeACoffee: faMugHot,

  // Misc
  globe: faGlobe,
  arrowRight: faChevronRight,
  link: faLink,
  external: faArrowUpRightFromSquare,
  image: faImage,
  // Audio
  play: faPlay,
  pause: faPause,
  music: faMusic,
  microphone: faMicrophone,
  // Chat
  hashtag: faHashtag,
  back: faChevronLeft,
  members: faUserGroup,
  refresh: faArrowsRotate,
} as const

export type IconName = keyof typeof ICON_MAP

/**
 * Predefined color variants for icons
 */
export const colorStyles = {
  inherit: '',
  primary: 'text-primary-500',
  muted: 'text-[var(--text-muted)]',
  // Reaction colors
  robot: 'text-primary-400',
  heart: 'text-pink-500',
  fire: 'text-orange-500',
  brain: 'text-violet-500',
  lightbulb: 'text-yellow-400',
  celebrate: 'text-amber-500',
  laugh: 'text-yellow-500',
  mindBlown: 'text-violet-400',
  // Status colors
  verified: 'text-primary-500',
  success: 'text-success-500',
  error: 'text-error-500',
  warning: 'text-warning-500',
} as const

export type IconColor = keyof typeof colorStyles

/**
 * Size presets for consistent icon sizing
 */
export const sizeStyles = {
  xs: 'text-xs',
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl',
  '2xl': 'text-2xl',
  '3xl': 'text-3xl',
  '4xl': 'text-4xl',
  '5xl': 'text-5xl',
  '6xl': 'text-6xl',
} as const

export type IconSize = keyof typeof sizeStyles

/**
 * Get the raw Font Awesome icon definition by name
 * Useful when you need to use FontAwesomeIcon directly
 */
export function getIconDefinition(name: IconName): IconDefinition {
  return ICON_MAP[name]
}

/**
 * Mapping of reaction types to icon names and colors
 */
export const REACTION_ICONS: Record<
  string,
  { icon: IconName; color: IconColor; label: string }
> = {
  robot_love: { icon: 'robot', color: 'robot', label: 'Robot Love' },
  robot: { icon: 'robot', color: 'robot', label: 'Robot Love' },
  mind_blown: { icon: 'mindBlown', color: 'mindBlown', label: 'Mind Blown' },
  brain: { icon: 'brain', color: 'brain', label: 'Mind Blown' },
  idea: { icon: 'lightbulb', color: 'lightbulb', label: 'Idea' },
  fire: { icon: 'fire', color: 'fire', label: 'Fire' },
  celebrate: { icon: 'celebrate', color: 'celebrate', label: 'Celebrate' },
  laugh: { icon: 'laugh', color: 'laugh', label: 'Laugh' },
  heart: { icon: 'heart', color: 'heart', label: 'Heart' },
}
