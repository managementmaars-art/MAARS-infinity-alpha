const { ccclass, property } = cc._decorator;
 
import WebUIRenderer from './WebUIRenderer';
import { withdrawExample1 } from './examples/withdrawExample1';

@ccclass
export default class WebUIExample extends cc.Component {
  @property(cc.Node)
  target: cc.Node = null;

  start() {
    const host = this.target || this.node;
    host.setAnchorPoint(0, 1);

    this.scheduleOnce(() => {

      let renderer = host.getComponent(WebUIRenderer);
      if (!renderer) {
        renderer = host.addComponent(WebUIRenderer);
      }

      renderer.render(withdrawExample1);
    })
  }
}
