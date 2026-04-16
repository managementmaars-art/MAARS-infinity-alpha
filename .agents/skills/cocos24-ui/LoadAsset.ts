const { ccclass } = cc._decorator

@ccclass
export default class LoadAsset extends cc.Component {
    static find(comp: cc.Component) {
        let parent = comp.node;
        while (parent) {
            const loadAsset = parent.getComponent(LoadAsset);
            if (loadAsset) {
                return loadAsset;
            }
            parent = parent.parent;
        }
        throw new Error('Cannot find LoadAsset component in parent nodes.');
    }
    private array: Array<cc.Asset> = []
    onDestroy() {
        this.array.forEach((asset) => {
            asset.decRef();
        })
        this.array = null;
    }
    load<T extends cc.Asset>(url: string, type: { prototype: cc.Asset }, end: (asset: T) => void) {
        cc.resources.load(url, type, (err, asset) => {
            if (err) {
                this.onLoadError(err);
            } else {
                this.onLoadComplete(asset);
            }
            if (this.array) {
                end(asset as T);
            }
        })
    }
    private onLoadComplete(asset: cc.Asset) {
        asset.addRef();
        if (this.array) {
            this.array.push(asset);
        } else {
            asset.decRef();
        }
    }
    private onLoadError(err: Error) {
        setTimeout(() => {
            throw err;
        })
    }
}
