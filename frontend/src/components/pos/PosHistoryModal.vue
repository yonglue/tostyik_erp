<template>
  <!-- 销售历史查询与快速退换货 -->
  <div v-if="visible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border border-slate-100 flex flex-col max-h-[85vh]">
      <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
        <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
          <span>📜 最近销售历史与退换货管理 (后端数据库持久化)</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
      </div>

      <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div
          v-for="order in orders"
          :key="order.dbId"
          class="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition-all flex flex-col gap-3"
        >
          <div class="flex items-center justify-between border-b border-slate-200/60 pb-2">
            <div>
              <span class="font-mono font-bold text-blue-600 text-xs mr-3">单号: {{ order.orderId }}</span>
              <span class="text-xs text-slate-500 font-semibold">客户: {{ order.clientName || '散客' }}</span>
              <span v-if="order.status === 'REFUNDED'" class="ml-2 bg-rose-100 text-rose-700 text-[10px] px-2 py-0.5 rounded font-bold">已退货</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-xs text-slate-400">{{ order.time }}</span>
              <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">{{ order.paymentMethod }}</span>
            </div>
          </div>

          <!-- 订单内商品列表 -->
          <div class="space-y-1">
            <div v-for="item in order.items" :key="item.oem" class="flex justify-between text-xs text-slate-700">
              <span>{{ item.name }} (OEM: {{ item.oem }}) x {{ item.quantity }}</span>
              <span class="font-mono">${{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between pt-2 border-t border-slate-200/40">
            <span class="text-xs font-bold text-slate-900">
              总计: ${{ order.totalUsd.toFixed(2) }} (Bs. {{ (order.totalUsd * order.bcvRate).toFixed(2) }})
            </span>
            <div class="flex gap-2">
              <button
                @click="$emit('reprint', order)"
                class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer"
              >
                🖨️ 补打小票
              </button>
              <button
                v-if="order.status !== 'REFUNDED'"
                @click="$emit('return', order.dbId)"
                class="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 rounded-xl text-xs font-bold transition-colors cursor-pointer"
              >
                🔄 申请退货/退款
              </button>
            </div>
          </div>
        </div>

        <div v-if="orders.length === 0" class="text-center py-16 text-slate-400 text-xs">
          暂无近期完成的销售订单记录
        </div>
      </div>

      <div class="p-4 bg-slate-50 border-t border-slate-100 text-right">
        <button @click="$emit('close')" class="px-5 py-2 bg-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-300 transition-colors cursor-pointer">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  orders: { type: Array, default: () => [] }
})

defineEmits(['close', 'reprint', 'return'])
</script>
