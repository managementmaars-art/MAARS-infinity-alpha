import UIManager from "./UIManager";

const { ccclass, property } = cc._decorator;

@ccclass
export default class UIState extends cc.Component {
    manager: UIManager = null;
    url: string = '';
    ui: cc.Node = null;
    data: any = null;
    loadUI(url: string) {
        this.url = url;
        this.manager.loadAsset.load<cc.Prefab>(url, cc.Prefab, (prefab) => {
            if (this.isValid && prefab) {
                const node = cc.instantiate(prefab);
                this.ui = node;
                this.node.addChild(node);
            }
        })
    }
    protected onDestroy(): void {
        this.ui?.destroy();
        this.ui = null;
    }
}
