const { ccclass } = cc._decorator;

@ccclass
export default class WebUIBackground extends cc.Component {
  colorHex = '#ffffff';
  radius = 0;

  onEnable() {
    this.updateGraphics();
  }

  updateGraphics() {
    const graphics = this.getComponent(cc.Graphics) || this.addComponent(cc.Graphics);
    graphics.clear();
    graphics.fillColor = this.parseColor(this.colorHex);

    const width = this.node.width || 1;
    const height = this.node.height || 1;
    const radius = Math.max(0, Math.min(this.radius, width * 0.5, height * 0.5));

    // 直接使用 Cocos 内置的 roundRect，保证圆角与 HTML border-radius 一致
    graphics.roundRect(0, -height, width, height, radius);
    graphics.fill();
  }

  private parseColor(value: string): cc.Color {
    const color = new cc.Color();
    return color.fromHEX(value);
  }
}
