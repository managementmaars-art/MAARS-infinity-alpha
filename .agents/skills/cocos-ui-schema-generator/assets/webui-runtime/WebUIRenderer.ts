const { ccclass, property } = cc._decorator;
         
import WebUIBackground from './WebUIBackground';
import { WebUILayoutEngine } from './layout';
import { mergeStyle } from './style';
import { WebUINodeSchema } from './types';

@ccclass
export default class WebUIRenderer extends cc.Component {
  @property
  autoRenderOnLoad = false;

  private _engine = new WebUILayoutEngine();
  private _schema: WebUINodeSchema | null = null;
  private _idNodeMap: { [id: string]: cc.Node } = {};

  onLoad() {
    if (this.autoRenderOnLoad && this._schema) {
      this.render(this._schema);
    }
  }

  render(schema: WebUINodeSchema) {
    this._schema = schema;
    this._idNodeMap = {};
    this.node.removeAllChildren();
    this.node.setAnchorPoint(0, 1);

    // schema 里所有数值按 360 逻辑像素编写
    // fitWidth 模式下：Canvas 逻辑宽 = designWidth，物理宽 = designWidth × DPR
    const designSize = cc.view.getDesignResolutionSize();
    const dpr = cc.view.getDevicePixelRatio();
    const physicalWidth = designSize.width * dpr;

    // layoutScale：逻辑坐标换算，用于布局引擎所有尺寸（padding/margin/width/height 等）
    const layoutScale = designSize.width / 360;
    // fontScale：物理像素换算，用于字体大小，保证清晰度
    const fontScale = physicalWidth / 360;

    this._engine.scale = layoutScale;

    // 1. 创建内容节点树
    const content = this.createNodeTree(schema, layoutScale, fontScale);

    // 2. 布局：宽度用逻辑坐标，高度强制 auto 让引擎根据子内容自动计算
    const logicWidth = designSize.width;
    const logicHeight = designSize.height;
    // autoHeight=true：忽略 root schema 的 height:'100%'，按子内容实际高度计算
    this._engine.layoutTree(content, schema, logicWidth, logicHeight, true);
    // 布局完成后从节点实际高度读取真实内容高度
    const contentHeight = content.height;

    // 4. 创建 ScrollView，大小 = 屏幕可见区域
    const scrollNode = new cc.Node('ScrollView');
    scrollNode.setAnchorPoint(0, 1);
    scrollNode.setContentSize(logicWidth, logicHeight);
    scrollNode.setPosition(0, 0);

    const scrollView = scrollNode.addComponent(cc.ScrollView);
    scrollView.horizontal = false;
    scrollView.vertical = true;
    scrollView.inertia = true;
    scrollView.brake = 0.75;
    scrollView.elastic = true;
    scrollView.bounceDuration = 0.23;

    // 5. 创建 view 遮罩节点（ScrollView 可见区域）
    const viewNode = new cc.Node('view');
    viewNode.setAnchorPoint(0, 1);
    viewNode.setContentSize(logicWidth, logicHeight);
    viewNode.setPosition(0, 0);
    viewNode.addComponent(cc.Mask);
    scrollNode.addChild(viewNode);

    // 6. content 挂到 view 下
    content.setAnchorPoint(0, 1);
    content.setPosition(0, 0);
    viewNode.addChild(content);

    // 7. 绑定 ScrollView 的 content
    scrollView.content = content;

    this.node.addChild(scrollNode);

    this.refreshBackgrounds(content);
  }

  getNodeById(id: string): cc.Node | null {
    return this._idNodeMap[id] || null;
  }

  getNodesByIds(ids: string[]): { [id: string]: cc.Node | null } {
    const result: { [id: string]: cc.Node | null } = {};
    for (let i = 0; i < ids.length; i++) {
      const id = ids[i];
      result[id] = this.getNodeById(id);
    }
    return result;
  }

  hasNodeId(id: string): boolean {
    return !!this._idNodeMap[id];
  }

  private createNodeTree(schema: WebUINodeSchema, layoutScale: number = 1, fontScale: number = 1): cc.Node {
    const node = new cc.Node(schema.name || schema.id || schema.type);
    const style = mergeStyle(schema.type, schema.style);

    if (schema.id) {
      if (this._idNodeMap[schema.id]) {
        cc.warn('[WebUIRenderer] duplicate schema id:', schema.id);
      }
      this._idNodeMap[schema.id] = node;
    }

    node.opacity = Math.floor((style.opacity != null ? style.opacity : 1) * 255);
    node.zIndex = style.zIndex || 0;
    node.setAnchorPoint(0, 1);
    node.setContentSize(0, 0);

    if (schema.type === 'text') {
      this.applyText(node, schema, fontScale);
    } else if (schema.type === 'image') {
      this.applyImage(node, schema);
    } else {
      this.applyView(node, schema, layoutScale);
    }

    const children = schema.children || [];
    for (let i = 0; i < children.length; i++) {
      node.addChild(this.createNodeTree(children[i], layoutScale, fontScale));
    }

    return node;
  }

  private applyView(node: cc.Node, schema: WebUINodeSchema, scale: number = 1) {
    const style = mergeStyle(schema.type, schema.style);
    if (!style.backgroundColor) {
      return;
    }

    const background = node.addComponent(WebUIBackground);
    background.colorHex = style.backgroundColor;
    background.radius = (style.borderRadius || 0) * scale;
  }

  private applyText(node: cc.Node, schema: WebUINodeSchema, scale: number = 1) {
    const label = node.addComponent(cc.Label);
    const style = mergeStyle(schema.type, schema.style);
    const fontSize = Math.round((style.fontSize || 20) * scale);
    const lineHeight = style.lineHeight
      ? Math.round(style.lineHeight * scale)
      : Math.ceil(fontSize * 1.4);

    node.setContentSize(0, 0);
    label.string = (schema.props && schema.props.text) || '';
    label.fontSize = fontSize;
    label.lineHeight = lineHeight;
    label.horizontalAlign = this.toLabelAlign(style.textAlign || 'left');
    label.verticalAlign = cc.Label.VerticalAlign.CENTER;
    label.overflow = style.whiteSpace === 'nowrap' ? cc.Label.Overflow.NONE : cc.Label.Overflow.RESIZE_HEIGHT;
    label.enableWrapText = style.whiteSpace !== 'nowrap';

    if (style.fontWeight && Number(style.fontWeight) >= 600) {
      label.enableBold = true;
    }

    node.color = this.parseColor(style.color || '#ffffff');
  }

  private applyImage(node: cc.Node, schema: WebUINodeSchema) {
    const sprite = node.addComponent(cc.Sprite);
    const src = schema.props && schema.props.src;
    if (!src) {
      return;
    }

    if (cc.resources) {
      cc.resources.load(src, cc.SpriteFrame, (error: Error, asset: cc.SpriteFrame) => {
        if (error) {
          cc.warn('[WebUIRenderer] image load failed:', src, error.message);
          return;
        }

        sprite.spriteFrame = asset;
      });
    } else {
      cc.warn('[WebUIRenderer] not resources bundle')
    }
  }

  private refreshBackgrounds(node: cc.Node) {
    const background = node.getComponent(WebUIBackground);
    if (background) {
      background.updateGraphics();
    }

    for (let i = 0; i < node.childrenCount; i++) {
      this.refreshBackgrounds(node.children[i]);
    }
  }

  private parseColor(value: string): cc.Color {
    const color = new cc.Color();
    return color.fromHEX(value);
  }

  private toLabelAlign(value: string): number {
    switch (value) {
      case 'center':
        return cc.Label.HorizontalAlign.CENTER;
      case 'right':
        return cc.Label.HorizontalAlign.RIGHT;
      case 'left':
      default:
        return cc.Label.HorizontalAlign.LEFT;
    }
  }
}
