import LoadAsset from "./LoadAsset";

const { ccclass, property, requireComponent } = cc._decorator;

@ccclass
@requireComponent(cc.Sprite)
export default class LoadSprite extends cc.Component {
    @property
    onLoadUrl: string = '';
    sprite: cc.Sprite = null;
    loadAsset: LoadAsset = null;
    protected onLoad(): void {
        this.sprite = this.node.getComponent(cc.Sprite);
        this.loadAsset = LoadAsset.find(this);
        if (this.onLoadUrl) {
            this.setUrl(this.onLoadUrl);
        }
    }
    setUrl(url: string) {
        this.loadAsset.load<cc.SpriteFrame>(url, cc.SpriteFrame, (spriteFrame) => {
            if (this.isValid) {
                this.sprite.spriteFrame = spriteFrame;
            }
        });
    }
}
