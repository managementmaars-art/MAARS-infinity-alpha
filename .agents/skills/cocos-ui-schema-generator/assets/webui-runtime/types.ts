export type WebUIValue = number | string;
export type WebUIBoxValue = number | [number, number, number, number]; 

export type WebUINodeType = 'view' | 'text' | 'image';
export type WebUIDisplay = 'flex' | 'none';
export type WebUIPosition = 'relative' | 'absolute';
export type WebUIFlexDirection = 'row' | 'column';
export type WebUIJustifyContent = 'flex-start' | 'center' | 'flex-end' | 'space-between' | 'space-around' | 'space-evenly';
export type WebUIAlignItems = 'flex-start' | 'center' | 'flex-end' | 'stretch' | 'baseline';
export type WebUIAlignSelf = 'auto' | 'flex-start' | 'center' | 'flex-end' | 'stretch' | 'baseline';
export type WebUIFlexWrap = 'nowrap' | 'wrap';
export type WebUITextAlign = 'left' | 'center' | 'right';
export type WebUIWhiteSpace = 'normal' | 'nowrap';
export type WebUIOverflow = 'visible' | 'hidden';
export type WebUIImageFit = 'fill' | 'contain' | 'cover' | 'none';

export interface WebUIStyle {
  display?: WebUIDisplay;
  position?: WebUIPosition;
  flexDirection?: WebUIFlexDirection;
  justifyContent?: WebUIJustifyContent;
  alignItems?: WebUIAlignItems;
  alignSelf?: WebUIAlignSelf;
  flexWrap?: WebUIFlexWrap;
  flexGrow?: number;
  flexShrink?: number;
  flexBasis?: WebUIValue;
  gap?: number;

  width?: WebUIValue;
  height?: WebUIValue;
  minWidth?: WebUIValue;
  minHeight?: WebUIValue;
  maxWidth?: WebUIValue;
  maxHeight?: WebUIValue;

  padding?: WebUIBoxValue;
  margin?: WebUIBoxValue;
  paddingTop?: number;
  paddingRight?: number;
  paddingBottom?: number;
  paddingLeft?: number;
  marginTop?: number;
  marginRight?: number;
  marginBottom?: number;
  marginLeft?: number;

  left?: WebUIValue;
  right?: WebUIValue;
  top?: WebUIValue;
  bottom?: WebUIValue;
  zIndex?: number;

  backgroundColor?: string;
  opacity?: number;
  borderRadius?: number;

  fontSize?: number;
  fontWeight?: number | string;
  color?: string;
  lineHeight?: number;
  textAlign?: WebUITextAlign;
  whiteSpace?: WebUIWhiteSpace;
  overflow?: WebUIOverflow;

  objectFit?: WebUIImageFit;
}

export interface WebUIProps {
  text?: string;
  src?: string;
  [key: string]: any;
}

export interface WebUINodeSchema {
  type: WebUINodeType;
  id?: string;
  name?: string;
  style?: WebUIStyle;
  props?: WebUIProps;
  children?: WebUINodeSchema[];
}

export interface WebUIEdgeInsets {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface WebUILayoutFrame {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface WebUILayoutResult {
  frame: WebUILayoutFrame;
  contentWidth: number;
  contentHeight: number;
}
