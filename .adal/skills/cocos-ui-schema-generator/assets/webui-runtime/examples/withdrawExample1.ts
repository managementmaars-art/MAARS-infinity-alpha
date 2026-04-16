import { WebUINodeSchema } from '../types';
 
export const withdrawExample1: WebUINodeSchema = {
  type: 'view',
  id: 'root',
  style: {
    width: '100%',
    height: '100%',
    backgroundColor: '#f5f5f5',
    flexDirection: 'column',
  },
  children: [
    // 1. 顶部返回区域
    {
      type: 'view',
      style: {
        width: '100%',
        padding: [16, 16, 0, 16],
      },
      children: [
        {
          type: 'text',
          props: { text: '‹' },
          style: { fontSize: 32, color: '#333333' }
        }
      ]
    },
    // 2. 打款信息区
    {
      type: 'view',
      style: {
        width: '100%',
        padding: [16, 20, 20, 20],
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center'
      },
      children: [
        // 左边文字
        {
          type: 'view',
          style: { flexDirection: 'column', gap: 6 },
          children: [
            {
              type: 'text',
              props: { text: '打款给 viv...' },
              style: { fontSize: 18, color: '#000000', fontWeight: 700 }
            },
            {
              type: 'text',
              props: { text: '打款方式：微信打款' },
              style: { fontSize: 13, color: '#999999' }
            }
          ]
        },
        // 右侧头像占位 (因为没有具体切图，这里用深色色块替代模拟图片)
        {
          type: 'view',
          style: {
            width: 48,
            height: 48,
            backgroundColor: '#1c1c3c', 
            borderRadius: 8
          },
          // 如果有真实图片可以使用: type: 'image', props: { src: 'xxx' }
        }
      ]
    },
    // 3. 底部主容器 (包含提现详情、任务卡、按钮)
    {
      type: 'view',
      style: {
        width: '100%',
        backgroundColor: '#ffffff',
        borderRadius: 16, // 目前 engine 实现是全局半径，先用整个圆角代替
        padding: [30, 20, 40, 20],
        flexDirection: 'column',
        flexGrow: 1,
      },
      children: [
        // 3.1 可提现金额标题
        {
          type: 'text',
          props: { text: '可提现金额' },
          style: { fontSize: 15, color: '#333333', marginBottom: 16 }
        },
        // 大字号金额展示区
        {
          type: 'view',
          style: {
            flexDirection: 'row',
            alignItems: 'baseline',
            marginBottom: 20
          },
          children: [
            { type: 'text', props: { text: '¥' }, style: { fontSize: 32, color: '#000000', fontWeight: 700, marginRight: 2 } },
            { type: 'text', props: { text: '40.00' }, style: { fontSize: 56, color: '#000000', fontWeight: 700 } }
          ]
        },
        // 分割线
        {
          type: 'view',
          style: { width: '100%', height: 1, backgroundColor: '#f0f0f0', marginBottom: 20 }
        },
        // 3.2 打款方信息
        {
          type: 'view',
          style: {
            width: '100%',
            flexDirection: 'row',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 20
          },
          children: [
            { type: 'text', props: { text: '打款方' }, style: { fontSize: 16, color: '#999999' } },
            { type: 'text', props: { text: '现金大转盘' }, style: { fontSize: 16, color: '#333333' } },
          ]
        },
        // 分割线
        {
          type: 'view',
          style: { width: '100%', height: 1, backgroundColor: '#f0f0f0', marginBottom: 30 }
        },
        // 3.3 任务卡片区 (包含阴影/深底色)
        {
          type: 'view',
          style: {
            width: '100%',
            backgroundColor: '#f6f6f9',  // 浅灰偏紫色背景色
            borderRadius: 12,
            padding: [24, 0, 24, 0],
            flexDirection: 'column',
            alignItems: 'center',
            marginBottom: 30
          },
          children: [
            // 限时胶囊
            {
              type: 'view',
              style: {
                backgroundColor: '#eaeaef',
                padding: [4, 12, 4, 12],
                borderRadius: 12,
                marginBottom: 16
              },
              children: [
                { type: 'text', props: { text: '限时04:58.8' }, style: { fontSize: 13, color: '#666666' } }
              ]
            },
            // 文案拼接 (部分黑色，部分绿色)
            {
              type: 'view',
              style: { flexDirection: 'row', alignItems: 'center', marginBottom: 24, gap: 4 },
              children: [
                { type: 'text', props: { text: '预计拉1人，' }, style: { fontSize: 16, color: '#333333', fontWeight: 700 } },
                { type: 'text', props: { text: '即将打款' }, style: { fontSize: 16, color: '#07c160', fontWeight: 700 } }
              ]
            },
            // 加号占位 () 
            // 当前圆角边框引擎不支持，用两个 View 套娃实现：灰色底 + 小一圈的白底，形成灰色边框效果
            {
              type: 'view',
              style: {
                width: 44,
                height: 44,
                borderRadius: 22,
                backgroundColor: '#cccccc', // 模拟边框颜色
                justifyContent: 'center',
                alignItems: 'center'
              },
              children: [
                {
                  type: 'view',
                  style: {
                    width: 42,
                    height: 42,
                    borderRadius: 21,
                    backgroundColor: '#fafafa', // 内部底色
                    justifyContent: 'center',
                    alignItems: 'center'
                  },
                  children: [
                    { type: 'text', props: { text: '+' }, style: { fontSize: 24, color: '#cccccc' } }
                  ]
                }
              ]
            }
          ]
        },
        // 3.4 占位伸展区：等价模拟 HTML 中按钮的 margin-top: auto
        {
          type: 'view',
          style: {
            width: '100%',
            flexGrow: 1,
          },
        },
        // 3.5 邀请按钮
        {
          type: 'view',
          style: {
            width: '100%',
            height: 50,
            backgroundColor: '#1bc35b', // 抢眼绿色
            borderRadius: 25,
            justifyContent: 'center',
            alignItems: 'center'
          },
          children: [
             { type: 'text', props: { text: '邀请好友加速提现' }, style: { fontSize: 17, color: '#ffffff', fontWeight: 700 } }
          ]
        }
      ]
    }
  ]
};
