const { ccclass, property } = cc._decorator;

// 请求信息接口
interface PendingRequest {
    requestId: string;
    amount: number;        // 正数表示增加，负数表示减少
    type: 'add' | 'subtract';
    timestamp: number;
}

@ccclass
export default class ModelValue extends cc.Component {
    on(type: string, callback: () => void, target?: any) {
        this.node.on(type, callback, target);
    }
    off(type: string, callback: () => void, target?: any) {
        this.node.off(type, callback, target);
    }
    // 确定的部分（默认值）
    private _certainValue: number = 0;

    // 所有进行中的不确定请求
    private _pendingRequests: Map<string, PendingRequest> = new Map();

    // 请求ID计数器
    private _requestIdCounter: number = 0;

    /**
     * 静态创建方法
     * @param name - 节点名称
     * @param initialValue - 初始确定值
     * @returns 创建的 ModelValue 实例
     */
    static create(name: string, initialValue: number): ModelValue {
        const node = new cc.Node(name);
        node.parent = cc.director.getScene();
        const modelValue = node.addComponent(ModelValue);
        modelValue.setCertainValue(initialValue);
        return modelValue;
    }

    // ========== 确定值相关方法 ==========

    /**
     * 设置确定值
     * @param value - 新的确定值
     */
    setCertainValue(value: number): void {
        this._certainValue = value;
        this.emitValueChanged();
    }

    /**
     * 获取确定值
     * @returns 当前确定值
     */
    get certainValue(): number {
        return this._certainValue;
    }

    /**
     * 增加确定值
     * @param amount - 要增加的金额
     */
    addCertainValue(amount: number): void {
        this._certainValue += amount;
        this.emitValueChanged();
    }

    /**
     * 减少确定值
     * @param amount - 要减少的金额
     */
    subtractCertainValue(amount: number): void {
        this._certainValue -= amount;
        this.emitValueChanged();
    }

    // ========== 核心计算逻辑 ==========

    /**
     * 获取所有进行中的减少请求的总金额（绝对值）
     * @private
     * @returns 减少请求总金额
     */
    private getTotalPendingSubtractAmount(): number {
        let total = 0;
        const requests = Array.from(this._pendingRequests.values());
        for (const request of requests) {
            if (request.type === 'subtract') {
                total += Math.abs(request.amount);
            }
        }
        return total;
    }

    /**
     * 获取剩余可确定的金额（确定值 - 所有进行中的减少请求）
     * @returns 剩余可确定金额
     */
    get remainingCertainAmount(): number {
        const totalPendingSubtract = this.getTotalPendingSubtractAmount();
        return Math.max(0, this._certainValue - totalPendingSubtract);
    }

    /**
     * 检查是否可以购买（考虑进行中的请求）
     * @param amount - 要购买的金额
     * @returns 是否可以购买
     */
    canPurchase(amount: number): boolean {
        return amount <= this.remainingCertainAmount;
    }

    /**
     * 获取当前总值（确定值 + 所有进行中的增加请求 - 所有进行中的减少请求）
     * @returns 当前总值
     */
    get totalValue(): number {
        let total = this._certainValue;
        const requests = Array.from(this._pendingRequests.values());
        for (const request of requests) {
            total += request.amount;
        }
        return total;
    }

    // ========== 请求管理方法 ==========

    /**
     * 生成唯一的请求ID
     * @private
     * @returns 生成的请求ID
     */
    private generateRequestId(): string {
        this._requestIdCounter++;
        return `req_${this._requestIdCounter}_${Date.now()}`;
    }

    /**
     * 开始一个增加请求
     * @param amount - 要增加的金额
     * @returns 请求ID
     */
    startAddRequest(amount: number): string {
        const requestId = this.generateRequestId();
        const request: PendingRequest = {
            requestId,
            amount,
            type: 'add',
            timestamp: Date.now()
        };

        this._pendingRequests.set(requestId, request);
        console.log(`开始增加请求 ${requestId}，金额: ${amount}`);
        this.node.emit('requestStarted', request);
        this.emitValueChanged();

        return requestId;
    }

    /**
     * 开始一个减少请求（购买/消费）
     * @param amount - 要减少的金额
     * @returns 请求ID，如果无法购买则返回null
     */
    startSubtractRequest(amount: number): string | null {
        // 检查是否可以购买
        if (!this.canPurchase(amount)) {
            console.warn(`无法购买，金额 ${amount} 超过剩余可确定金额 ${this.remainingCertainAmount}`);
            return null;
        }

        const requestId = this.generateRequestId();
        const request: PendingRequest = {
            requestId,
            amount: -amount, // 负值表示减少
            type: 'subtract',
            timestamp: Date.now()
        };

        this._pendingRequests.set(requestId, request);
        console.log(`开始减少请求 ${requestId}，金额: ${amount}，剩余可确定金额: ${this.remainingCertainAmount}`);
        this.node.emit('requestStarted', request);
        this.emitValueChanged();

        return requestId;
    }

    /**
     * 获取所有进行中的请求
     * @returns 进行中的请求数组
     */
    get pendingRequests(): PendingRequest[] {
        return Array.from(this._pendingRequests.values());
    }

    /**
     * 检查是否有进行中的请求
     * @returns 是否有进行中的请求
     */
    get hasPendingRequests(): boolean {
        return this._pendingRequests.size > 0;
    }

    /**
     * 获取进行中的请求数量
     * @returns 请求数量
     */
    get pendingRequestCount(): number {
        return this._pendingRequests.size;
    }

    /**
     * 获取指定请求
     * @param requestId - 请求ID
     * @returns 请求信息，如果不存在则返回undefined
     */
    getRequest(requestId: string): PendingRequest | undefined {
        return this._pendingRequests.get(requestId);
    }

    // ========== 请求结果处理 ==========

    /**
     * 请求成功（确定化）
     * @param requestId - 请求ID
     * @returns 是否成功处理
     */
    requestSuccess(requestId: string): boolean {
        const request = this._pendingRequests.get(requestId);
        if (!request) {
            console.warn(`请求 ${requestId} 不存在或已完成`);
            return false;
        }

        // 将请求金额合并到确定值中
        this._certainValue += request.amount;

        console.log(`请求 ${requestId} 成功，金额 ${request.amount} 已确定化，新确定值: ${this._certainValue}`);
        this.node.emit('requestSuccess', {
            ...request,
            newCertainValue: this._certainValue
        });

        // 移除请求
        this._pendingRequests.delete(requestId);
        this.emitValueChanged();

        return true;
    }

    /**
     * 请求失败（丢弃）
     * @param requestId - 请求ID
     * @returns 是否成功处理
     */
    requestFailed(requestId: string): boolean {
        const request = this._pendingRequests.get(requestId);
        if (!request) {
            console.warn(`请求 ${requestId} 不存在或已完成`);
            return false;
        }

        console.log(`请求 ${requestId} 失败，金额 ${request.amount} 被丢弃`);
        this.node.emit('requestFailed', request);

        // 移除请求
        this._pendingRequests.delete(requestId);
        this.emitValueChanged();

        return true;
    }

    /**
     * 取消请求
     * @param requestId - 请求ID
     * @returns 是否成功处理
     */
    cancelRequest(requestId: string): boolean {
        const request = this._pendingRequests.get(requestId);
        if (!request) {
            console.warn(`请求 ${requestId} 不存在或已完成`);
            return false;
        }

        console.log(`请求 ${requestId} 被取消，金额 ${request.amount} 被丢弃`);
        this.node.emit('requestCancelled', request);

        // 移除请求
        this._pendingRequests.delete(requestId);
        this.emitValueChanged();

        return true;
    }

    /**
     * 取消所有请求
     */
    cancelAllRequests(): void {
        const requests = Array.from(this._pendingRequests.values());
        this._pendingRequests.clear();

        for (const request of requests) {
            console.log(`请求 ${request.requestId} 被取消`);
            this.node.emit('requestCancelled', request);
        }

        this.emitValueChanged();
    }

    // ========== 其他计算方法 ==========

    /**
     * 获取最小可能值（考虑所有减少请求都失败的情况）
     * @returns 最小可能值
     */
    get minPossibleValue(): number {
        return this._certainValue;
    }

    /**
     * 获取最大可能值（考虑所有增加请求都成功的情况）
     * @returns 最大可能值
     */
    get maxPossibleValue(): number {
        let max = this._certainValue;
        const requests = Array.from(this._pendingRequests.values());
        for (const request of requests) {
            if (request.amount > 0) { // 只考虑增加请求
                max += request.amount;
            }
        }
        return max;
    }

    /**
     * 获取进行中的增加请求总金额
     * @returns 增加请求总金额
     */
    get totalPendingAddAmount(): number {
        let total = 0;
        const requests = Array.from(this._pendingRequests.values());
        for (const request of requests) {
            if (request.type === 'add') {
                total += request.amount;
            }
        }
        return total;
    }

    /**
     * 获取进行中的减少请求总金额
     * @returns 减少请求总金额
     */
    get totalPendingSubtractAmount(): number {
        return this.getTotalPendingSubtractAmount();
    }

    // ========== 工具方法 ==========

    /**
     * 触发值变化事件
     * @private
     */
    private emitValueChanged(): void {
        this.node.emit('valueChanged', {
            certainValue: this._certainValue,
            totalValue: this.totalValue,
            remainingCertainAmount: this.remainingCertainAmount,
            pendingRequestCount: this.pendingRequestCount,
            totalPendingAddAmount: this.totalPendingAddAmount,
            totalPendingSubtractAmount: this.totalPendingSubtractAmount
        });
    }

    /**
     * 重置所有值
     */
    reset(): void {
        this._certainValue = 0;
        this._pendingRequests.clear();
        this._requestIdCounter = 0;
        this.emitValueChanged();
    }

    /**
     * 获取状态信息
     * @returns 完整的状态信息对象
     */
    getStateInfo(): any {
        return {
            certainValue: this._certainValue,
            remainingCertainAmount: this.remainingCertainAmount,
            totalValue: this.totalValue,
            pendingRequests: this.pendingRequests,
            pendingRequestCount: this.pendingRequestCount,
            canPurchaseExamples: {
                canPurchase10: this.canPurchase(10),
                canPurchase50: this.canPurchase(50),
                canPurchase100: this.canPurchase(100)
            }
        };
    }
}
