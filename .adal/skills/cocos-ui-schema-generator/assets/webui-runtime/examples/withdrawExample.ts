import { WebUINodeSchema } from '../types';
 
export const withdrawExample: WebUINodeSchema = {
  type: 'view',
  id: 'root',
  style: {
    width: '100%',
    height: '100%',
    backgroundColor: '#f5f5f5',
  },
  children: [
    {
      type: 'view',
      id: 'status-bar',
      style: {
        height: 24,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: [0, 12, 0, 12],
        backgroundColor: '#07c160',
      },
      children: [
        {
          type: 'text',
          props: { text: '11:38' },
          style: { fontSize: 14, color: '#ffffff', fontWeight: 600 },
        },
        {
          type: 'view',
          style: { flexDirection: 'row', alignItems: 'center', gap: 4 },
          children: [
            {
              type: 'text',
              props: { text: '5G' },
              style: { fontSize: 12, color: '#ffffff', fontWeight: 600 },
            },
            {
              type: 'text',
              props: { text: '电量' },
              style: { fontSize: 12, color: '#ffffff', fontWeight: 600 },
            },
          ],
        },
      ],
    },
    {
      type: 'view',
      id: 'nav-bar',
      style: {
        height: 44,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#07c160',
      },
      children: [
        {
          type: 'text',
          props: { text: '提现到微信' },
          style: { fontSize: 17, color: '#ffffff', fontWeight: 600 },
        },
        {
          type: 'text',
          props: { text: '‹' },
          style: {
            position: 'absolute',
            left: 12,
            top: 10,
            fontSize: 20,
            color: '#ffffff',
          },
        },
      ],
    },
    {
      type: 'view',
      id: 'content',
      style: {
        width: '100%',
        padding: [0, 16, 0, 16],
        gap: 12,
      },
      children: [
        {
          type: 'view',
          style: {
            width: '100%',
            marginTop: 12,
            padding: 16,
            borderRadius: 8,
            backgroundColor: '#ffffff',
            flexDirection: 'row',
            alignItems: 'center',
            gap: 8,
          },
          children: [
            { type: 'text', props: { text: '提现至：' }, style: { fontSize: 15, color: '#666666' } },
            {
              type: 'view',
              style: {
                width: 20,
                height: 20,
                borderRadius: 4,
                backgroundColor: '#07c160',
                justifyContent: 'center',
                alignItems: 'center',
              },
              children: [
                { type: 'text', props: { text: '微' }, style: { fontSize: 12, color: '#ffffff' } },
              ],
            },
            { type: 'text', props: { text: '微信' }, style: { fontSize: 15, color: '#333333' } },
            { type: 'text', props: { text: '（账户：owe...）' }, style: { fontSize: 14, color: '#999999' } },
          ],
        },
        {
          type: 'view',
          style: {
            width: '100%',
            padding: [20, 16, 20, 16],
            borderRadius: 8,
            backgroundColor: '#ffffff',
            gap: 12,
          },
          children: [
            { type: 'text', props: { text: '待提现金额' }, style: { fontSize: 14, color: '#666666' } },
            {
              type: 'view',
              style: {
                flexDirection: 'row',
                alignItems: 'flex-start',
              },
              children: [
                { type: 'text', props: { text: '¥' }, style: { fontSize: 24, color: '#333333', marginRight: 2 } },
                { type: 'text', props: { text: '25' }, style: { fontSize: 36, color: '#333333', fontWeight: 700 } },
              ],
            },
            {
              type: 'view',
              style: {
                width: '100%',
                paddingTop: 16,
                gap: 12,
              },
              children: [
                {
                  type: 'view',
                  style: { width: '100%', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
                  children: [
                    { type: 'text', props: { text: '创建时间' }, style: { fontSize: 14, color: '#999999' } },
                    { type: 'text', props: { text: '2026-03-10 11:38:19' }, style: { fontSize: 14, color: '#333333' } },
                  ],
                },
                {
                  type: 'view',
                  style: { width: '100%', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
                  children: [
                    { type: 'text', props: { text: '打款方式' }, style: { fontSize: 14, color: '#999999' } },
                    {
                      type: 'view',
                      style: { flexDirection: 'row', alignItems: 'center', gap: 4 },
                      children: [
                        { type: 'text', props: { text: '✓' }, style: { fontSize: 14, color: '#07c160' } },
                        { type: 'text', props: { text: '微信打款' }, style: { fontSize: 14, color: '#07c160' } },
                      ],
                    },
                  ],
                },
                {
                  type: 'view',
                  style: { width: '100%', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
                  children: [
                    { type: 'text', props: { text: '已获得金额' }, style: { fontSize: 14, color: '#999999' } },
                    { type: 'text', props: { text: '25元' }, style: { fontSize: 14, color: '#ff5722' } },
                  ],
                },
                {
                  type: 'view',
                  style: { width: '100%', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
                  children: [
                    { type: 'text', props: { text: '待获得金额' }, style: { fontSize: 14, color: '#999999' } },
                    { type: 'text', props: { text: '25元' }, style: { fontSize: 14, color: '#ff5722' } },
                  ],
                },
              ],
            },
          ],
        },
        {
          type: 'view',
          style: {
            width: '100%',
            borderRadius: 8,
            backgroundColor: '#ffffff',
            overflow: 'hidden',
          },
          children: [
            {
              type: 'view',
              style: {
                flexDirection: 'row',
                alignItems: 'center',
                gap: 8,
                padding: [12, 16, 12, 16],
              },
              children: [
                {
                  type: 'view',
                  style: {
                    width: 24,
                    height: 24,
                    borderRadius: 4,
                    backgroundColor: '#ff5a5f',
                    justifyContent: 'center',
                    alignItems: 'center',
                  },
                  children: [
                    { type: 'text', props: { text: '拼' }, style: { fontSize: 12, color: '#ffffff', fontWeight: 700 } },
                  ],
                },
                {
                  type: 'text',
                  props: { text: '奖励通知-来自现金大转盘' },
                  style: { fontSize: 14, color: '#333333', fontWeight: 500 },
                },
              ],
            },
            {
              type: 'view',
              style: {
                padding: [20, 16, 20, 16],
                alignItems: 'center',
                gap: 8,
              },
              children: [
                { type: 'text', props: { text: '奖励金额' }, style: { fontSize: 14, color: '#666666' } },
                {
                  type: 'view',
                  style: { flexDirection: 'row', alignItems: 'flex-start' },
                  children: [
                    { type: 'text', props: { text: '¥' }, style: { fontSize: 20, color: '#333333', marginRight: 2 } },
                    { type: 'text', props: { text: '25' }, style: { fontSize: 32, color: '#333333', fontWeight: 700 } },
                  ],
                },
                {
                  type: 'view',
                  style: {
                    width: '100%',
                    marginTop: 20,
                    gap: 8,
                  },
                  children: [
                    {
                      type: 'view',
                      style: { width: '100%', flexDirection: 'row', justifyContent: 'space-between' },
                      children: [
                        { type: 'text', props: { text: '收款账户' }, style: { fontSize: 13, color: '#999999' } },
                        { type: 'text', props: { text: 'owen' }, style: { fontSize: 13, color: '#666666' } },
                      ],
                    },
                    {
                      type: 'view',
                      style: { width: '100%', flexDirection: 'row', justifyContent: 'space-between' },
                      children: [
                        { type: 'text', props: { text: '转账备注' }, style: { fontSize: 13, color: '#999999' } },
                        { type: 'text', props: { text: '来自现金大转盘' }, style: { fontSize: 13, color: '#666666' } },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },
        {
          type: 'text',
          props: { text: '累计50元即可全部提现' },
          style: {
            marginTop: 40,
            fontSize: 13,
            color: '#999999',
            textAlign: 'center',
          },
        },
      ],
    },
  ],
};
