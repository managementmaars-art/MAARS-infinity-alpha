import LoadSprite from "./LoadSprite";
import { UIModel } from "./UIModelExample";

const { ccclass, property } = cc._decorator;

@ccclass
export default class UIExample extends cc.Component {
    // 1. 声明引用的组件
    @property(cc.Label)
    title_label: cc.Label = null;
    @property(cc.Label)
    count_label: cc.Label = null;
    @property(cc.Node)
    progress_bar: cc.Node = null;
    @property(LoadSprite)
    icon_sprite: LoadSprite = null;

    // 数据引用
    data: UIModel = null;
    isListening: boolean = false;

    // 2. setData 方法 - UI 初始化入口
    setData(data: UIModel) {
        this.data = data;
        this.initListen();
        this.updateUI();
    }

    // 3. 事件监听管理
    initListen() {
        if (this.isListening) return;
        this.isListening = true;
        this.data.value.on('valueChanged', this.updateUI, this);
    }

    onDestroy() {
        if (!this.isListening) return;
        this.isListening = false;
        this.data.value.off('valueChanged', this.updateUI, this);
    }

    // 更新 UI 显示
    updateUI() {
        this.title_label.string = this.data.title;
        this.count_label.string = `${this.data.value.certainValue}`;
        this.progress_bar.width = 100 * (this.data.value.certainValue / this.data.maxValue);
    }

    // 4. click 统一处理点击事件
    click(target: cc.Event.EventTouch) {
        switch (target.currentTarget.name) {
            case 'btn_confirm':
                this.onConfirmClick();
                break;
            case 'btn_cancel':
                this.onCancelClick();
                break;
            default:
                break;
        }
    }

    onConfirmClick() {
        // 确认按钮处理逻辑
    }

    onCancelClick() {
        // 取消按钮处理逻辑
    }
}
