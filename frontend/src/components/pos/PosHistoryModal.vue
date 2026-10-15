<!-- src/components/pos/PosHistoryModal.vue -->
<template>
  <div v-if="visible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-3xl w-full overflow-hidden border border-slate-100 flex flex-col max-h-[88vh]">
      
      <!-- 顶部标题栏 -->
      <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
        <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
          <span>📜 {{ t.posHistoryTitle || '最近销售历史与退换货管理' }}</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- 🔍 搜索与日期筛选栏 -->
      <div class="p-4 border-b border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <input 
            v-model="searchQuery" 
            type="text" 
            :placeholder="t.posSearchOrderPlaceholder || '输入订单编号 / 客户名称搜索...'" 
            class="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 outline-none focus:border-blue-500 font-mono shadow-xs"
          />
        </div>
        <div class="w-full sm:w-48">
          <input 
            v-model="selectedDate" 
            type="date" 
            class="w-full bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-xs text-slate-800 outline-none focus:border-blue-500 font-mono shadow-xs cursor-pointer"
          />
        </div>
        <button 
          v-if="searchQuery || selectedDate"
          @click="searchQuery = ''; selectedDate = ''"
          class="px-3 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer"
        >
          {{ t.btnClearFilter || '清除筛选' }}
        </button>
      </div>

      <!-- 订单列表区 -->
      <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div
          v-for="order in filteredOrders"
          :key="order.dbId"
          class="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition-all flex flex-col gap-3"
        >
          <div class="flex items-center justify-between border-b border-slate-200/60 pb-2">
            <div>
              <span class="font-mono font-bold text-blue-600 text-xs mr-3">{{ t.posOrderNo || '单号' }}: {{ order.orderId || order.order_no }}</span>
              <span class="text-xs text-slate-500 font-semibold">{{ t.posClient || '客户' }}: {{ order.clientName || order.client_name || '散客' }}</span>
              <span v-if="order.status === 'REFUNDED'" class="ml-2 bg-rose-100 text-rose-700 text-[10px] px-2 py-0.5 rounded font-bold">已退货</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-xs text-slate-400 font-mono">{{ order.time || order.created_at }}</span>
              <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">{{ order.paymentMethod || order.payment_method }}</span>
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
              {{ t.posTotal || '总计' }}: ${{ (order.totalUsd || order.total_usd || 0).toFixed(2) }} (Bs. {{ ((order.totalUsd || order.total_usd || 0) * (order.bcvRate || order.bcv_rate || 1)).toFixed(2) }})
            </span>
            
            <!-- 操作按钮组 (补打小票、PDF下载、申请退货) -->
            <div class="flex gap-2">
              <button
                @click="$emit('reprint', order)"
                class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1"
              >
                <span>🖨️</span> {{ t.posReprintTicket || '补打小票' }}
              </button>
              
              <!-- 🌟 升级：携带当前订单编号请求对应语言的 PDF 下载 -->
              <a
                :href="apiUrl(`/api/quotation/pdf/download?quotation_no=${order.orderId || order.order_no}`)"
                target="_blank"
                class="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1 shadow-2xs"
              >
                <span>📥</span> PDF
              </a>

              <button
                v-if="order.status !== 'REFUNDED'"
                @click="$emit('return', order.dbId || order.id)"
                class="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1"
              >
                <span>🔄</span> {{ t.posRequestReturn || '申请退货/退款' }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="filteredOrders.length === 0" class="text-center py-16 text-slate-400 text-xs">
          {{ t.posNoHistory || '暂无符合条件的销售订单记录' }}
        </div>
      </div>

      <div class="p-4 bg-slate-50 border-t border-slate-100 text-right">
        <button @click="$emit('close')" class="px-5 py-2 bg-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-300 transition-colors cursor-pointer">
          {{ t.btnCancel || '关闭' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from '../../composables/useI18n'
import { apiUrl } from '../../utils/api'

const { t } = useI18n()

const props = defineProps({
  visible: { type: Boolean, default: false },
  orders: { type: Array, default: () => [] }
})

defineEmits(['close', 'reprint', 'return'])

// ── 搜索与日期过滤状态 ──
const searchQuery = ref('')
const selectedDate = ref('')

const filteredOrders = computed(() => {
  if (!props.orders) return []
  return props.orders.filter(order => {
    const orderNo = (order.orderId || order.order_no || '').toLowerCase()
    const clientName = (order.clientName || order.client_name || '').toLowerCase()
    const query = searchQuery.value.toLowerCase().trim()
    
    const matchesQuery = !query || orderNo.includes(query) || clientName.includes(query)
    
    // 日期匹配（支持订单时间字符串中包含所选日期，例如 2026-10-15）
    const orderTimeStr = (order.time || order.created_at || '')
    const matchesDate = !selectedDate.value || orderTimeStr.includes(selectedDate.value)
    
    return matchesQuery && matchesDate
  })
})
</script>