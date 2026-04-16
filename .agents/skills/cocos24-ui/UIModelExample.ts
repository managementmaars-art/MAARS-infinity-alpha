import ModelValue from "./ModelValue";

/**
 * UI 数据模型示例
 * 定义 UI 所需的所有数据字段
 */
export class UIModel {
    /** 唯一标识 */
    id: number;
    /** 标题文本 */
    title: string = '';
    /** 是否解锁 */
    isUnlock: boolean = false;
    /** 可监听的数值类型 */
    value: ModelValue;
    /** 最大值 */
    maxValue: number = 100;
    /** 嵌套子模型 */
    items: SubModel[] = [];
}

/**
 * 子数据模型示例
 */
export class SubModel {
    /** 序号 */
    index: number = 0;
    /** 名称 */
    name: string = '';
    /** 是否已领取 */
    isReceived: boolean = false;
    /** 图标路径 */
    iconUrl: string = '';
}
