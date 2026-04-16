import { clampSize, isAutoValue, mergeStyle, normalizeBoxValue, resolveValue } from './style';
import { WebUILayoutFrame, WebUILayoutResult, WebUINodeSchema, WebUIStyle } from './types';        

interface ChildLayoutItem {
  node: cc.Node;
  schema: WebUINodeSchema;
  style: WebUIStyle;
  marginTop: number;
  marginRight: number;
  marginBottom: number;
  marginLeft: number;
  width: number;
  height: number;
}

export class WebUILayoutEngine {
  /** 逻辑像素 → 设计分辨率像素的缩放系数，由 WebUIRenderer 注入 */
  scale: number = 1;

  layoutTree(node: cc.Node, schema: WebUINodeSchema, availableWidth: number, availableHeight: number, autoHeight: boolean = false): WebUILayoutResult {
    const style = this.scaleStyle(mergeStyle(schema.type, schema.style));
    const padding = normalizeBoxValue(style, 'padding');

    let width = resolveValue(style.width, availableWidth);
    // autoHeight=true 时忽略 schema 里的 height（如 '100%'），强制按子内容计算
    let height = autoHeight ? null : resolveValue(style.height, availableHeight);

    if (width == null) {
      width = schema.type === 'text'
        ? this.measureTextNode(node, schema, 0, false, style).width
        : availableWidth;
    }

    if (height == null) {
      if (schema.type === 'text') {
        const shouldConstrain = this.shouldConstrainText(node, schema, style, width);
        height = this.measureTextNode(node, schema, width, shouldConstrain, style).height;
      } else if (autoHeight) {
        // 根据子内容实际高度计算；根节点 autoHeight 场景下至少撑满可视区，才能为 flexGrow 留出可分配空间
        height = this.measureViewHeight(node, schema, style, width, availableHeight);
        height = Math.max(height, availableHeight);
      } else {
        height = availableHeight;
      }
    }

    width = clampSize(width, style.minWidth, style.maxWidth, availableWidth);
    height = clampSize(height, style.minHeight, style.maxHeight, availableHeight);

    this.applyFrame(node, { x: 0, y: 0, width, height });

    const contentWidth = Math.max(0, width - padding.left - padding.right);
    const contentHeight = Math.max(0, height - padding.top - padding.bottom);

    if (schema.type === 'view' && style.display !== 'none') {
      this.layoutChildren(node, schema, style, contentWidth, contentHeight, padding.left, padding.top);
    }

    return {
      frame: { x: 0, y: 0, width, height },
      contentWidth,
      contentHeight,
    };
  }

  private layoutChildren(
    parentNode: cc.Node,
    schema: WebUINodeSchema,
    style: WebUIStyle,
    contentWidth: number,
    contentHeight: number,
    offsetX: number,
    offsetY: number,
  ) {
    const children = parentNode.children;
    const childSchemas = schema.children || [];
    const gap = style.gap || 0;
    const direction = style.flexDirection || 'column';
    const normalItems: ChildLayoutItem[] = [];
    const absoluteItems: ChildLayoutItem[] = [];

    for (let i = 0; i < children.length; i++) {
      const childNode = children[i];
      const childSchema = childSchemas[i];
      if (!childSchema) {
        continue;
      }

      const childStyle = this.scaleStyle(mergeStyle(childSchema.type, childSchema.style));
      if (childStyle.display === 'none') {
        childNode.active = false;
        continue;
      }

      childNode.active = true;
      const margin = normalizeBoxValue(childStyle, 'margin');
      const measured = this.measureChild(
        childNode,
        childSchema,
        childStyle,
        contentWidth,
        contentHeight,
        direction,
        margin,
        style,
      );

      const item: ChildLayoutItem = {
        node: childNode,
        schema: childSchema,
        style: childStyle,
        marginTop: margin.top,
        marginRight: margin.right,
        marginBottom: margin.bottom,
        marginLeft: margin.left,
        width: measured.width,
        height: measured.height,
      };

      if (childStyle.position === 'absolute') {
        absoluteItems.push(item);
      } else {
        normalItems.push(item);
      }
    }

    if (direction === 'row') {
      this.layoutRow(normalItems, style, contentWidth, contentHeight, offsetX, offsetY, gap);
    } else {
      this.layoutColumn(normalItems, style, contentWidth, contentHeight, offsetX, offsetY, gap);
    }

    for (let i = 0; i < absoluteItems.length; i++) {
      this.layoutAbsolute(absoluteItems[i], contentWidth, contentHeight, offsetX, offsetY);
    }
  }

  private layoutColumn(
    items: ChildLayoutItem[],
    style: WebUIStyle,
    contentWidth: number,
    contentHeight: number,
    offsetX: number,
    offsetY: number,
    gap: number,
  ) {
    this.applyColumnFlexGrow(items, contentHeight, gap);
    const totalHeight = this.getColumnTotalHeight(items, gap);
    const distribution = this.resolveDistribution(style.justifyContent || 'flex-start', contentHeight, totalHeight, items.length);
    let cursorY = offsetY + distribution.start;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      cursorY += item.marginTop;
      const x = offsetX + this.resolveCrossAxisX(style, item, contentWidth);
      this.applyLayoutToItem(item, x, cursorY, item.width, item.height);
      cursorY += item.height + item.marginBottom;
      if (i < items.length - 1) {
        cursorY += gap + distribution.extraGap;
      }
    }
  }

  private layoutRow(
    items: ChildLayoutItem[],
    style: WebUIStyle,
    contentWidth: number,
    contentHeight: number,
    offsetX: number,
    offsetY: number,
    gap: number,
  ) {
    this.applyRowFlexGrow(items, contentWidth, gap);
    const totalWidth = this.getRowTotalWidth(items, gap);
    const distribution = this.resolveDistribution(style.justifyContent || 'flex-start', contentWidth, totalWidth, items.length);
    const baselineAlign = (style.alignItems || 'stretch') === 'baseline';
    const rowBaseline = baselineAlign ? this.getRowBaseline(items) : 0;
    let cursorX = offsetX + distribution.start;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      cursorX += item.marginLeft;
      const y = baselineAlign
        ? offsetY + this.resolveBaselineY(item, rowBaseline)
        : offsetY + this.resolveCrossAxisY(style, item, contentHeight);
      this.applyLayoutToItem(item, cursorX, y, item.width, item.height);
      cursorX += item.width + item.marginRight;
      if (i < items.length - 1) {
        cursorX += gap + distribution.extraGap;
      }
    }
  }

  private layoutAbsolute(item: ChildLayoutItem, parentWidth: number, parentHeight: number, offsetX: number, offsetY: number) {
    const style = item.style;
    let width = item.width;
    let height = item.height;

    const left = resolveValue(style.left, parentWidth);
    const right = resolveValue(style.right, parentWidth);
    const top = resolveValue(style.top, parentHeight);
    const bottom = resolveValue(style.bottom, parentHeight);

    if (left != null && right != null && isAutoValue(style.width)) {
      width = Math.max(0, parentWidth - left - right);
    }

    if (top != null && bottom != null && isAutoValue(style.height)) {
      height = Math.max(0, parentHeight - top - bottom);
    }

    const x = offsetX + (left != null ? left : (right != null ? parentWidth - right - width : 0));
    const y = offsetY + (top != null ? top : (bottom != null ? parentHeight - bottom - height : 0));

    this.applyLayoutToItem(item, x, y, width, height);
  }

  private applyLayoutToItem(item: ChildLayoutItem, x: number, y: number, width: number, height: number) {
    this.applyFrame(item.node, { x, y, width, height });

    // text 节点：布局宽度确定后，如果设置了 textAlign center/right，
    // 需要将 Label 切换为 RESIZE_HEIGHT 模式，否则 horizontalAlign 在 NONE 模式下不生效。
    // 但对于没有设置 textAlign（默认 left）的 text，保持 NONE 避免不必要的换行。
    if (item.schema.type === 'text') {
      const textAlign = item.style.textAlign || 'left';
      if (textAlign !== 'left') {
        const label = item.node.getComponent(cc.Label);
        if (label) {
          label.overflow = cc.Label.Overflow.RESIZE_HEIGHT;
          // @ts-ignore
          label._forceUpdateRenderData();
        }
      }
    }

    if (item.schema.type === 'view' && item.style.display !== 'none') {
      const childPadding = normalizeBoxValue(item.style, 'padding');
      this.layoutChildren(
        item.node,
        item.schema,
        item.style,
        Math.max(0, width - childPadding.left - childPadding.right),
        Math.max(0, height - childPadding.top - childPadding.bottom),
        childPadding.left,
        childPadding.top,
      );
    }

    const background = item.node.getComponent('WebUIBackground') as any;
    if (background && background.updateGraphics) {
      background.updateGraphics();
    }
  }

  private measureChild(
    node: cc.Node,
    schema: WebUINodeSchema,
    style: WebUIStyle,
    parentWidth: number,
    parentHeight: number,
    parentDirection: 'row' | 'column',
    margin: { top: number; right: number; bottom: number; left: number },
    parentStyle: WebUIStyle,
    allowStretchMeasure: boolean = true,
  ) {
    let width = resolveValue(style.width, parentWidth);
    let height = resolveValue(style.height, parentHeight);
    const stretch = allowStretchMeasure && this.resolveAlign(parentStyle, style) === 'stretch';


    if (schema.type === 'text') {
      if (width == null) {
        // column 方向且父容器 alignItems=stretch 时，text 和 CSS 块级元素一样撑满父容器宽度
        if (parentDirection === 'column' && stretch) {
          width = Math.max(0, parentWidth - margin.left - margin.right);
        } else {
          const natural = this.measureTextNode(node, schema, 0, false, style);
          width = natural.width;
        }
      }
      if (height == null) {
        const shouldConstrain = this.shouldConstrainText(node, schema, style, width);
        const measured = this.measureTextNode(node, schema, width, shouldConstrain, style);
        height = measured.height;
      }
    }

    if (schema.type === 'image') {
      if (width == null) {
        width = 0;
      }
      if (height == null) {
        height = 0;
      }
    }

    if (schema.type === 'view') {
      if (width == null) {
        if (parentDirection === 'column' && stretch) {
          width = Math.max(0, parentWidth - margin.left - margin.right);
        } else {
          width = this.measureViewWidth(node, schema, style, parentWidth, parentHeight);
        }
      }

      if (height == null) {
        if (parentDirection === 'row' && stretch) {
          height = Math.max(0, parentHeight - margin.top - margin.bottom);
        } else {
          height = this.measureViewHeight(node, schema, style, width, parentHeight);
        }
      }
    }

    width = width != null ? width : 0;
    height = height != null ? height : 0;

    width = clampSize(width, style.minWidth, style.maxWidth, parentWidth);
    height = clampSize(height, style.minHeight, style.maxHeight, parentHeight);

    return { width, height };
  }

  private measureViewWidth(
    node: cc.Node,
    schema: WebUINodeSchema,
    style: WebUIStyle,
    parentWidth: number,
    parentHeight: number,
  ): number {
    const padding = normalizeBoxValue(style, 'padding');
    const children = schema.children || [];

    if (children.length === 0) {
      return padding.left + padding.right;
    }

    const contentBaseWidth = Math.max(0, parentWidth - padding.left - padding.right);
    const direction = style.flexDirection || 'column';

    if (direction === 'row') {
      let totalWidth = padding.left + padding.right;
      for (let i = 0; i < children.length; i++) {
        const child = children[i];
        const childStyle = this.scaleStyle(mergeStyle(child.type, child.style));
        if (childStyle.position === 'absolute' || childStyle.display === 'none') {
          continue;
        }
        const childMargin = normalizeBoxValue(childStyle, 'margin');
        const childNode = node.children[i];
        const measured = this.measureChild(
          childNode,
          child,
          childStyle,
          contentBaseWidth,
          parentHeight,
          'row',
          childMargin,
          style,
          false,
        );
        totalWidth += childMargin.left + measured.width + childMargin.right;
        if (i < children.length - 1) {
          totalWidth += style.gap || 0;
        }
      }
      return totalWidth;
    }

    let maxWidth = 0;
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      const childStyle = this.scaleStyle(mergeStyle(child.type, child.style));
      if (childStyle.position === 'absolute' || childStyle.display === 'none') {
        continue;
      }
      const childMargin = normalizeBoxValue(childStyle, 'margin');
      const childNode = node.children[i];
      const measured = this.measureChild(
        childNode,
        child,
        childStyle,
        contentBaseWidth,
        parentHeight,
        'column',
        childMargin,
        style,
        false,
      );
      maxWidth = Math.max(maxWidth, childMargin.left + measured.width + childMargin.right);
    }

    return padding.left + maxWidth + padding.right;
  }

  private measureViewHeight(
    node: cc.Node,
    schema: WebUINodeSchema,
    style: WebUIStyle,
    width: number,
    parentHeight: number,
  ): number {
    const padding = normalizeBoxValue(style, 'padding');
    const children = schema.children || [];
    const contentWidth = Math.max(0, width - padding.left - padding.right);

    if (children.length === 0) {
      return padding.top + padding.bottom;
    }

    if ((style.flexDirection || 'column') === 'row') {
      let maxHeight = 0;
      for (let i = 0; i < children.length; i++) {
        const child = children[i];
        const childStyle = this.scaleStyle(mergeStyle(child.type, child.style));
        if (childStyle.position === 'absolute' || childStyle.display === 'none') {
          continue;
        }
        const childMargin = normalizeBoxValue(childStyle, 'margin');
        const childNode = node.children[i];
        const measured = this.measureChild(
          childNode,
          child,
          childStyle,
          contentWidth,
          parentHeight,
          'row',
          childMargin,
          style,
          false,
        );
        maxHeight = Math.max(maxHeight, childMargin.top + measured.height + childMargin.bottom);
      }
      return padding.top + maxHeight + padding.bottom;
    }

    let totalHeight = padding.top + padding.bottom;
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      const childStyle = this.scaleStyle(mergeStyle(child.type, child.style));
      if (childStyle.position === 'absolute' || childStyle.display === 'none') {
        continue;
      }
      const childMargin = normalizeBoxValue(childStyle, 'margin');
      const childNode = node.children[i];
      const measured = this.measureChild(
        childNode,
        child,
        childStyle,
        contentWidth,
        parentHeight,
        'column',
        childMargin,
        style,
        false,
      );
      totalHeight += childMargin.top + measured.height + childMargin.bottom;
      if (i < children.length - 1) {
        totalHeight += style.gap || 0;
      }
    }

    return totalHeight;
  }

  /**
   * 将 schema 中的逻辑像素值缩放为设计分辨率像素值。
   * 百分比字符串和 null/undefined 原样返回，只对数字生效。
   */
  private s(value: number): number;
  private s(value: string): string;
  private s(value: number | string | undefined): number | string | undefined;
  private s(value: any): any {
    if (typeof value === 'number') {
      return value * this.scale;
    }
    return value;
  }

  /** 缩放 WebUIStyle 中所有固定数值字段，返回新的 style 对象 */
  private scaleStyle(style: WebUIStyle): WebUIStyle {
    const sc = this.scale;
    if (sc === 1) {
      return style;
    }

    const scaled: WebUIStyle = { ...style };

    // 尺寸
    if (typeof scaled.width === 'number')     { scaled.width     = scaled.width     * sc; }
    if (typeof scaled.height === 'number')    { scaled.height    = scaled.height    * sc; }
    if (typeof scaled.minWidth === 'number')  { scaled.minWidth  = scaled.minWidth  * sc; }
    if (typeof scaled.minHeight === 'number') { scaled.minHeight = scaled.minHeight * sc; }
    if (typeof scaled.maxWidth === 'number')  { scaled.maxWidth  = scaled.maxWidth  * sc; }
    if (typeof scaled.maxHeight === 'number') { scaled.maxHeight = scaled.maxHeight * sc; }

    // 间距
    if (typeof scaled.gap === 'number') { scaled.gap = scaled.gap * sc; }

    // padding
    if (typeof scaled.padding === 'number') {
      scaled.padding = scaled.padding * sc;
    } else if (Array.isArray(scaled.padding)) {
      scaled.padding = scaled.padding.map(v => v * sc) as [number, number, number, number];
    }
    if (typeof scaled.paddingTop    === 'number') { scaled.paddingTop    = scaled.paddingTop    * sc; }
    if (typeof scaled.paddingRight  === 'number') { scaled.paddingRight  = scaled.paddingRight  * sc; }
    if (typeof scaled.paddingBottom === 'number') { scaled.paddingBottom = scaled.paddingBottom * sc; }
    if (typeof scaled.paddingLeft   === 'number') { scaled.paddingLeft   = scaled.paddingLeft   * sc; }

    // margin
    if (typeof scaled.margin === 'number') {
      scaled.margin = scaled.margin * sc;
    } else if (Array.isArray(scaled.margin)) {
      scaled.margin = scaled.margin.map(v => v * sc) as [number, number, number, number];
    }
    if (typeof scaled.marginTop    === 'number') { scaled.marginTop    = scaled.marginTop    * sc; }
    if (typeof scaled.marginRight  === 'number') { scaled.marginRight  = scaled.marginRight  * sc; }
    if (typeof scaled.marginBottom === 'number') { scaled.marginBottom = scaled.marginBottom * sc; }
    if (typeof scaled.marginLeft   === 'number') { scaled.marginLeft   = scaled.marginLeft   * sc; }

    // 定位
    if (typeof scaled.left   === 'number') { scaled.left   = scaled.left   * sc; }
    if (typeof scaled.right  === 'number') { scaled.right  = scaled.right  * sc; }
    if (typeof scaled.top    === 'number') { scaled.top    = scaled.top    * sc; }
    if (typeof scaled.bottom === 'number') { scaled.bottom = scaled.bottom * sc; }

    // 字体
    if (typeof scaled.fontSize    === 'number') { scaled.fontSize    = scaled.fontSize    * sc; }
    if (typeof scaled.lineHeight  === 'number') { scaled.lineHeight  = scaled.lineHeight  * sc; }
    if (typeof scaled.borderRadius === 'number') { scaled.borderRadius = scaled.borderRadius * sc; }

    return scaled;
  }

  private measureTextNode(node: cc.Node, schema: WebUINodeSchema, availableWidth: number, constrained: boolean, scaledStyle?: WebUIStyle): cc.Size {
    const label = node.getComponent(cc.Label);
    const style = scaledStyle || this.scaleStyle(mergeStyle(schema.type, schema.style));
    if (!label) {
      const text = (schema.props && schema.props.text) || '';
      const fontSize = (style.fontSize) || 20;
      const width = Math.ceil(text.length * fontSize * 0.55);
      const height = Math.ceil(fontSize * 1.4);
      return cc.size(constrained && availableWidth > 0 ? Math.min(width, availableWidth) : width, height);
    }

    label.string = (schema.props && schema.props.text) || '';
    label.fontSize = style.fontSize || label.fontSize;
    label.lineHeight = style.lineHeight || Math.ceil((style.fontSize || label.fontSize || 20) * 1.4);
    label.enableWrapText = style.whiteSpace !== 'nowrap';

    const shouldWrap = constrained && availableWidth > 0 && style.whiteSpace !== 'nowrap';
    if (shouldWrap) {
      node.width = availableWidth;
      label.overflow = cc.Label.Overflow.RESIZE_HEIGHT;
    } else {
      label.overflow = cc.Label.Overflow.NONE;
      node.width = 0;
      node.height = 0;
    }

    // @ts-ignore
    label._forceUpdateRenderData();

    let width = node.width;
    let height = node.height;

    if (!shouldWrap && availableWidth > 0 && width > availableWidth) {
      width = availableWidth;
    }

    if (!shouldWrap && height <= 0) {
      height = label.lineHeight || Math.ceil((style.fontSize || 20) * 1.4);
    }

    return cc.size(width, height);
  }

  private applyFrame(node: cc.Node, frame: WebUILayoutFrame) {
    node.setAnchorPoint(0, 1);
    node.setContentSize(frame.width, frame.height);
    node.setPosition(frame.x, -frame.y);
  }

  private getColumnTotalHeight(items: ChildLayoutItem[], gap: number): number {
    if (items.length === 0) {
      return 0;
    }

    let total = 0;
    for (let i = 0; i < items.length; i++) {
      total += items[i].marginTop + items[i].height + items[i].marginBottom;
      if (i < items.length - 1) {
        total += gap;
      }
    }
    return total;
  }

  private applyColumnFlexGrow(items: ChildLayoutItem[], containerHeight: number, gap: number) {
    const freeSpace = containerHeight - this.getColumnTotalHeight(items, gap);
    if (freeSpace <= 0) {
      return;
    }

    let totalGrow = 0;
    for (let i = 0; i < items.length; i++) {
      totalGrow += Math.max(0, items[i].style.flexGrow || 0);
    }

    if (totalGrow <= 0) {
      return;
    }

    let remainingSpace = freeSpace;
    let remainingGrow = totalGrow;

    for (let i = 0; i < items.length; i++) {
      const grow = Math.max(0, items[i].style.flexGrow || 0);
      if (grow <= 0) {
        continue;
      }

      const extra = remainingGrow > grow
        ? freeSpace * (grow / totalGrow)
        : remainingSpace;

      items[i].height = Math.max(0, items[i].height + extra);
      remainingSpace -= extra;
      remainingGrow -= grow;
    }
  }

  private getRowTotalWidth(items: ChildLayoutItem[], gap: number): number {
    if (items.length === 0) {
      return 0;
    }

    let total = 0;
    for (let i = 0; i < items.length; i++) {
      total += items[i].marginLeft + items[i].width + items[i].marginRight;
      if (i < items.length - 1) {
        total += gap;
      }
    }
    return total;
  }

  private applyRowFlexGrow(items: ChildLayoutItem[], containerWidth: number, gap: number) {
    const freeSpace = containerWidth - this.getRowTotalWidth(items, gap);
    if (freeSpace <= 0) {
      return;
    }

    let totalGrow = 0;
    for (let i = 0; i < items.length; i++) {
      totalGrow += Math.max(0, items[i].style.flexGrow || 0);
    }

    if (totalGrow <= 0) {
      return;
    }

    let remainingSpace = freeSpace;
    let remainingGrow = totalGrow;

    for (let i = 0; i < items.length; i++) {
      const grow = Math.max(0, items[i].style.flexGrow || 0);
      if (grow <= 0) {
        continue;
      }

      const extra = remainingGrow > grow
        ? freeSpace * (grow / totalGrow)
        : remainingSpace;

      items[i].width = Math.max(0, items[i].width + extra);
      remainingSpace -= extra;
      remainingGrow -= grow;
    }
  }

  private resolveDistribution(justifyContent: string, containerSize: number, contentSize: number, itemCount: number) {
    const free = Math.max(0, containerSize - contentSize);
    switch (justifyContent) {
      case 'center':
        return { start: free * 0.5, extraGap: 0 };
      case 'flex-end':
        return { start: free, extraGap: 0 };
      case 'space-between':
        return { start: 0, extraGap: itemCount > 1 ? free / (itemCount - 1) : 0 };
      case 'space-around':
        return { start: itemCount > 0 ? free / itemCount / 2 : 0, extraGap: itemCount > 0 ? free / itemCount : 0 };
      case 'space-evenly':
        return { start: itemCount > 0 ? free / (itemCount + 1) : 0, extraGap: itemCount > 0 ? free / (itemCount + 1) : 0 };
      case 'flex-start':
      default:
        return { start: 0, extraGap: 0 };
    }
  }

  private resolveCrossAxisX(style: WebUIStyle, item: ChildLayoutItem, containerWidth: number): number {
    const align = this.resolveAlign(style, item.style);
    switch (align) {
      case 'center':
        return (containerWidth - item.width) * 0.5;
      case 'flex-end':
        return containerWidth - item.width - item.marginRight;
      case 'stretch':
      case 'flex-start':
      default:
        return item.marginLeft;
    }
  }

  private resolveCrossAxisY(style: WebUIStyle, item: ChildLayoutItem, containerHeight: number): number {
    const align = this.resolveAlign(style, item.style);
    switch (align) {
      case 'center':
        return (containerHeight - item.height) * 0.5;
      case 'flex-end':
        return containerHeight - item.height - item.marginBottom;
      case 'baseline':
      case 'stretch':
      case 'flex-start':
      default:
        return item.marginTop;
    }
  }

  private getRowBaseline(items: ChildLayoutItem[]) {
    let baseline = 0;
    for (let i = 0; i < items.length; i++) {
      baseline = Math.max(baseline, items[i].marginTop + this.getItemBaseline(items[i]));
    }
    return baseline;
  }

  private resolveBaselineY(item: ChildLayoutItem, rowBaseline: number) {
    return rowBaseline - this.getItemBaseline(item);
  }

  private getItemBaseline(item: ChildLayoutItem) {
    if (item.schema.type === 'text') {
      const fontSize = item.style.fontSize || item.height || 0;
      const lineHeight = item.style.lineHeight || item.height || Math.ceil(fontSize * 1.4);
      const baselineRatio = 0.8;
      const textBaseline = Math.min(lineHeight, fontSize * baselineRatio + Math.max(0, lineHeight - fontSize) * 0.5);
      return textBaseline;
    }

    return item.height;
  }

  private resolveAlign(parentStyle: WebUIStyle, childStyle: WebUIStyle) {
    return childStyle.alignSelf && childStyle.alignSelf !== 'auto'
      ? childStyle.alignSelf
      : (parentStyle.alignItems || 'stretch');
  }

  private shouldConstrainText(node: cc.Node, schema: WebUINodeSchema, style: WebUIStyle, width: number) {
    if (style.whiteSpace === 'nowrap') {
      return false;
    }

    if (width <= 0) {
      return false;
    }

    const naturalWidth = this.measureTextNode(node, schema, 0, false, style).width;
    return naturalWidth > width + 1;
  }
}
