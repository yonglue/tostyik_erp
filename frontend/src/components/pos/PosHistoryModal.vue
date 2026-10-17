<!-- src/components/pos/PosHistoryModal.vue -->
<template>
  <div v-if="visible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
    <!-- 🌟 优化：给外层弹窗固定一个更舒适的宽度和最小高度，防止有无数据时大小跳动 -->
    <div class="bg-white rounded-3xl shadow-2xl max-w-3xl w-full h-[82vh] max-h-[850px] overflow-hidden border border-slate-100 flex flex-col">
      
      <!-- 顶部标题栏 -->
      <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80 shrink-0">
        <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
          <span>📜 {{ t.posHistoryTitle || '最近销售历史与退换货管理' }}</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- 🔍 搜索与日期筛选栏 -->
      <div class="p-4 border-b border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row gap-2.5 items-center shrink-0">
        <div class="flex-1 relative w-full">
          <input 
            v-model="searchQuery" 
            type="text" 
            :placeholder="t.posSearchOrderPlaceholder || '输入订单编号 / 客户名称搜索...'" 
            class="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 outline-none focus:border-blue-500 font-mono shadow-xs"
          />
        </div>

        <div class="flex items-center gap-2 w-full sm:w-auto">
          <!-- 日期选择框 -->
          <input 
            v-model="selectedDate" 
            type="date" 
            class="bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 outline-none focus:border-blue-500 font-mono shadow-xs cursor-pointer"
          />

          <!-- 快捷：今日按钮 -->
          <button 
            @click="setTodayFilter"
            :class="isTodaySelected ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'"
            class="px-3 py-2 border rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap shadow-xs"
          >
            📅 今日
          </button>

          <!-- 快捷：查看全部按钮 -->
          <button 
            @click="showAllHistory"
            :class="!selectedDate && !searchQuery ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'"
            class="px-3 py-2 border rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap shadow-xs"
          >
            🌐 全部历史
          </button>
        </div>
      </div>

      <!-- 订单列表区：🌟 强制设置 flex-1 与 min-h，确保无论有无数据，弹窗空间绝对稳定不收缩 -->
      <div class="flex-1 overflow-y-auto p-4 space-y-3 min-h-[420px] flex flex-col">
        <template v-if="filteredOrders.length > 0">
          <div
            v-for="order in filteredOrders"
            :key="order.dbId || order.id"
            class="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition-all flex flex-col gap-3 shrink-0"
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
              
              <!-- 操作按钮组 -->
              <div class="flex gap-2">
                <button
                  @click="$emit('reprint', order)"
                  class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1"
                >
                  <span>🖨️</span> {{ t.posReprintTicket || '补打小票' }}
                </button>
                
                <button
                  @click="downloadPdf(order.orderId || order.order_no)"
                  class="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1 shadow-2xs"
                >
                  <span>📥</span> PDF
                </button>

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
        </template>

        <!-- 暂无数据时的优雅占位，完美撑开高度不跳动 -->
        <div v-else class="flex-1 flex flex-col items-center justify-center py-20 text-slate-400 text-xs">
          <span class="text-3xl mb-2">📭</span>
          <span>{{ selectedDate ? `📅 ${selectedDate} 暂无历史销售记录` : (t.posNoHistory || '暂无符合条件的销售订单记录') }}</span>
        </div>
      </div>

      <!-- 底部统计与关闭栏 -->
      <div class="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between shrink-0">
        <span class="text-xs text-slate-500 font-mono">
          共找到 <strong class="text-slate-800">{{ filteredOrders.length }}</strong> 笔订单
        </span>
        <button @click="$emit('close')" class="px-5 py-2 bg-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-300 transition-colors cursor-pointer">
          {{ t.btnCancel || '关闭' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from '../../composables/useI18n'
import { apiFetch } from '../../utils/api'

const { t } = useI18n()

const props = defineProps({
  visible: { type: Boolean, default: false },
  orders: { type: Array, default: () => [] }
})

defineEmits(['close', 'reprint', 'return'])

// 获取浏览器本地设备的 YYYY-MM-DD
const getTodayString = () => {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 智能纠偏时区解析函数（将服务器超前的时间往回拨 4 小时对齐委内瑞拉当地）
const parseToLocalDateStr = (timeStr) => {
  if (!timeStr) return ''
  let cleanStr = timeStr.replace(/\//g, '-')
  if (cleanStr.includes(' ') || cleanStr.includes('T')) {
    const isoStr = cleanStr.includes('T') ? cleanStr : cleanStr.replace(' ', 'T')
    const d = new Date(isoStr)
    if (!isNaN(d.getTime())) {
      const venezuelaTime = new Date(d.getTime() - 4 * 3600 * 1000)
      const year = venezuelaTime.getFullYear()
      const month = String(venezuelaTime.getMonth() + 1).padStart(2, '0')
      const day = String(venezuelaTime.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
  }
  return cleanStr.substring(0, 10)
}

const searchQuery = ref('')
const selectedDate = ref(getTodayString())

const isTodaySelected = computed(() => selectedDate.value === getTodayString())

const setTodayFilter = () => {
  selectedDate.value = getTodayString()
  searchQuery.value = ''
}

const showAllHistory = () => {
  selectedDate.value = ''
  searchQuery.value = ''
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    selectedDate.value = getTodayString()
    searchQuery.value = ''
  }
})

const filteredOrders = computed(() => {
  if (!props.orders) return []
  return props.orders.filter(order => {
    const orderNo = (order.orderId || order.order_no || '').toLowerCase()
    const clientName = (order.clientName || order.client_name || '').toLowerCase()
    const query = searchQuery.value.toLowerCase().trim()
    
    const matchesQuery = !query || orderNo.includes(query) || clientName.includes(query)
    
    if (!selectedDate.value) return matchesQuery

    const orderLocalDate = parseToLocalDateStr(order.time || order.created_at)
    
    return matchesQuery && (orderLocalDate === selectedDate.value)
  })
})

const downloadPdf = async (orderNo) => {
  try {
    const res = await apiFetch(`/api/quotation/pdf/download?quotation_no=${orderNo}`)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || '下载 PDF 失败')
    }
    const blob = await res.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    window.open(blobUrl, '_blank')
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl)
    }, 10000)
  } catch (error) {
    console.error('PDF 下载异常:', error)
    alert(`❌ 无法生成订单 PDF: ${error.message}`)
  }
}
</script>