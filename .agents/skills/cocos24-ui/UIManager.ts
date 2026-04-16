import LoadAsset from "./LoadAsset"
import UIState from "./UIState"

const { ccclass, property } = cc._decorator

@ccclass
export default class UIManager extends cc.Component {
    private static _instance: UIManager = null;
    static get instance() {
        return this._instance;
    }

    @property(LoadAsset)
    loadAsset: LoadAsset = null

    @property(cc.Node)
    black_background: cc.Node = null;

    private array: Array<UIState> = []

    protected onLoad(): void {
        UIManager._instance = this;
    }

    protected onDestroy(): void {
        UIManager._instance = null;
    }

    showUI<T>(name: string, data?: T) {
        const uiState = this.addComponent(UIState)
        this.array.push(uiState)
        uiState.manager = this;
        uiState.data = data;
        uiState.loadUI(`ui/${name}`);
        this.black_background.active = true;
    }

    hideUI(name: string) {
        const url = `ui/${name}`;
        const uiState = this.array.find(v => v.url == url);
        if (uiState) {
            uiState.destroy();
            this.array.splice(this.array.indexOf(uiState), 1);
        } else {
            throw new Error("hideUI not find ui:" + url);
        }
        if (this.array.length == 0) {
            this.black_background.active = false;
        }
    }

    hideAllUI() {
        this.array.forEach(v => v.destroy());
        this.array.length = 0;
        this.black_background.active = false;
    }

    isShowUI(name: string) {
        return this.array.some(v => v.url == `ui/${name}`)
    }

    getUIdata<T>(ui: cc.Node): T {
        const uiState = this.array.find(v => v.ui == ui);
        if (uiState) {
            return uiState.data as T;
        }
        throw new Error("getUIdata not find ui:" + ui.name);
    }

    clickBackground() {
        
    }
}
