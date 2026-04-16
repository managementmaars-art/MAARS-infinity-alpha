import { WebUIEdgeInsets, WebUIStyle, WebUIValue } from './types';

export const DEFAULT_VIEW_STYLE: WebUIStyle = {
  display: 'flex',
  position: 'relative',
  flexDirection: 'column',
  justifyContent: 'flex-start',
  alignItems: 'stretch',
  alignSelf: 'auto',
  flexWrap: 'nowrap',
  flexGrow: 0,
  flexShrink: 1,
  flexBasis: 'auto',
  gap: 0,
  padding: 0,
  margin: 0,
  zIndex: 0,
  opacity: 1,
  overflow: 'visible',
};

export const DEFAULT_TEXT_STYLE: WebUIStyle = {
  position: 'relative',
  margin: 0,
  padding: 0,
  zIndex: 0,
  opacity: 1,
  fontSize: 20,
  color: '#ffffff',
  textAlign: 'left',
  whiteSpace: 'normal',
  overflow: 'visible',
};

export const DEFAULT_IMAGE_STYLE: WebUIStyle = {
  position: 'relative',
  margin: 0,
  padding: 0,
  zIndex: 0,
  opacity: 1,
  objectFit: 'fill',
};

export function getDefaultStyle(type: string): WebUIStyle {
  switch (type) {
    case 'text':
      return { ...DEFAULT_TEXT_STYLE };
    case 'image':
      return { ...DEFAULT_IMAGE_STYLE };
    case 'view':
    default:
      return { ...DEFAULT_VIEW_STYLE };
  }
}

export function mergeStyle(type: string, style?: WebUIStyle): WebUIStyle {
  return {
    ...getDefaultStyle(type),
    ...(style || {}),
  };
}

export function normalizeBoxValue(style: WebUIStyle, key: 'padding' | 'margin'): WebUIEdgeInsets {
  const base = style[key];
  let top = 0;
  let right = 0;
  let bottom = 0;
  let left = 0;

  if (typeof base === 'number') {
    top = right = bottom = left = base;
  } else if (Array.isArray(base)) {
    top = base[0] || 0;
    right = base[1] || 0;
    bottom = base[2] || 0;
    left = base[3] || 0;
  }

  if (key === 'padding') {
    top = style.paddingTop != null ? style.paddingTop : top;
    right = style.paddingRight != null ? style.paddingRight : right;
    bottom = style.paddingBottom != null ? style.paddingBottom : bottom;
    left = style.paddingLeft != null ? style.paddingLeft : left;
  } else {
    top = style.marginTop != null ? style.marginTop : top;
    right = style.marginRight != null ? style.marginRight : right;
    bottom = style.marginBottom != null ? style.marginBottom : bottom;
    left = style.marginLeft != null ? style.marginLeft : left;
  }

  return { top, right, bottom, left };
}

export function isPercentValue(value?: WebUIValue): boolean {
  return typeof value === 'string' && value.endsWith('%');
}

export function isAutoValue(value?: WebUIValue): boolean {
  return value == null || value === 'auto';
}

export function parsePercent(value: string): number {
  return parseFloat(value.replace('%', '')) / 100;
}

export function resolveValue(value: WebUIValue | undefined, base: number): number | null {
  if (value == null) {
    return null;
  }

  if (typeof value === 'number') {
    return value;
  }

  if (value === 'auto') {
    return null;
  }

  if (isPercentValue(value)) {
    return base * parsePercent(value);
  }

  const parsed = parseFloat(value);
  return Number.isNaN(parsed) ? null : parsed;
}

export function clampSize(value: number, min?: WebUIValue, max?: WebUIValue, base: number = 0): number {
  let next = value;
  const minValue = resolveValue(min, base);
  const maxValue = resolveValue(max, base);

  if (minValue != null) {
    next = Math.max(next, minValue);
  }

  if (maxValue != null) {
    next = Math.min(next, maxValue);
  }

  return next;
}
