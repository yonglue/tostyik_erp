<!-- src/components/pos/PosHistoryModal.vue -->
<template>
  <div v-if="visible" @click.self="$emit('close')" class="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
    <div class="bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-5xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
      
      <!-- 头部 -->
      <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
        <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
          <span>📜 {{ tExt.title }}</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- 筛选区 -->
      <div class="p-4 border-b border-slate-200/60 bg-white/40 shrink-0 flex flex-wrap gap-4 items-center">
        <div class="relative flex-1 min-w-[200px]">
          <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
          <input v-model="searchQuery" type="text" :placeholder="tExt.searchPlaceholder" class="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-xs outline-none focus:border-blue-500 font-bold text-slate-900 transition-colors" />
        </div>
        
        <div class="flex items-center gap-2">
          <input type="date" v-model="filterDate" class="bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-xs outline-none focus:border-blue-500 font-mono font-bold text-slate-700" />
          <button @click="filterDate = todayStr" class="bg-blue-600 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-sm cursor-pointer hover:bg-blue-700 transition-colors">{{ tExt.todayBtn }}</button>
          <button @click="filterDate = ''" class="bg-slate-100 hover:bg-slate-200 text-slate-600 px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition-colors">{{ tExt.allBtn }}</button>
        </div>
      </div>

      <!-- 列表区 -->
      <div class="flex-1 overflow-y-auto p-5 bg-white/20 space-y-3">
        <div v-for="order in filteredOrders" :key="order.dbId" class="bg-white/90 p-4 rounded-2xl border border-slate-200/80 hover:bg-white transition-all flex flex-wrap items-center justify-between gap-4 shadow-2xs">
          <div class="space-y-1">
            <div class="font-black text-sm text-slate-900 flex items-center gap-2">
              <span class="text-blue-600 font-mono">{{ order.orderId }}</span>
              <span>👤 {{ order.clientName }}</span>
            </div>
            <div class="text-xs text-slate-500 font-mono">{{ order.time }}</div>
          </div>
          
          <div class="flex items-center gap-6">
            <div class="text-right">
              <div class="text-sm font-black text-emerald-600 font-mono">$ {{ Number(order.totalUsd || 0).toFixed(2) }}</div>
              <div class="text-[10px] text-slate-500 font-bold uppercase">{{ getPaymentMethodLabel(order.paymentMethod) }}</div>
            </div>
            <div class="flex items-center gap-2">
              <button @click="$emit('reprint', order)" class="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 border border-indigo-100 rounded-lg text-xs font-bold transition-colors cursor-pointer">{{ tExt.btnReprint }}</button>
              <button @click="openReturnModal(order.dbId)" class="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-100 rounded-lg text-xs font-bold transition-colors cursor-pointer">{{ tExt.btnReturn }}</button>
            </div>
          </div>
        </div>

        <div v-if="filteredOrders.length === 0" class="flex flex-col items-center justify-center py-20 text-slate-400">
          <span class="text-5xl mb-3">📭</span>
          <span class="text-sm font-bold">{{ filterDate ? `${filterDate} ${tExt.emptyDateMsg}` : tExt.emptyAllMsg }}</span>
        </div>
      </div>

      <!-- 底部 -->
      <div class="p-5 bg-white/80 border-t border-slate-200/60 flex items-center justify-between shrink-0">
        <span class="text-xs text-slate-500 font-bold">{{ tExt.found }} <strong class="text-slate-900">{{ filteredOrders.length }}</strong> {{ tExt.orders }}</span>
        <button @click="$emit('close')" class="px-6 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ tExt.btnClose }}</button>
      </div>

    </div>
  </div>

  <!-- 🌟 退货确认弹窗 -->
  <ConfirmDialog
    :visible="returnModalVisible"
    overlay-class="bg-slate-900/40"
    :title="tExt.btnReturn"
    :message="tExt.confirmReturnMsg"
    :cancel-text="t.common.cancel"
    :confirm-text="tExt.btnReturn"
    @cancel="returnModalVisible = false"
    @confirm="executeReturn"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from 'lucide-vue-next'
import { useI18n } from '../../composables/useI18n'
import ConfirmDialog from '../ConfirmDialog.vue'

const props = defineProps({
  visible: Boolean,
  orders: Array
})
const emit = defineEmits(['close', 'reprint', 'return'])

const { t, currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '最近销售历史与退换货管理' : isEs ? 'Historial Reciente y Devoluciones' : 'Recent Sales & Returns',
    searchPlaceholder: isZh ? '输入订单编号 / 客户名称搜索...' : isEs ? 'Buscar por Nro. de Orden / Cliente...' : 'Search by Order No. / Client...',
    todayBtn: isZh ? '今日' : isEs ? 'Hoy' : 'Today',
    allBtn: isZh ? '全部历史' : isEs ? 'Todo el Historial' : 'All History',
    btnReprint: isZh ? '补打小票' : isEs ? 'Reimprimir' : 'Reprint',
    btnReturn: isZh ? '申请退货' : isEs ? 'Devolver' : 'Return',
    emptyDateMsg: isZh ? '暂无历史销售记录' : isEs ? 'Sin registros de ventas' : 'No sales records found',
    emptyAllMsg: isZh ? '暂无所有历史记录' : isEs ? 'No hay historial' : 'No history found',
    found: isZh ? '共找到' : isEs ? 'Encontrados' : 'Found',
    orders: isZh ? '笔订单' : isEs ? 'pedidos' : 'orders',
    btnClose: isZh ? '关闭' : isEs ? 'Cerrar' : 'Close',
    confirmReturnMsg: isZh ? '确认执行退货处理？该操作会自动将商品库存回滚至仓库。' : isEs ? '¿Confirmar devolución? El inventario se restaurará automáticamente.' : 'Confirm return? Inventory will be restored automatically.'
  }
})

// 支付方式翻译
const getPaymentMethodLabel = (method) => {
  if (!method) return '-'
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  const m = String(method).toUpperCase()
  if (m.includes('CASH_USD')) return isZh ? '现金 USD' : isEs ? 'Efectivo USD' : 'Cash USD'
  if (m.includes('CASH_BS')) return isZh ? '现金 Bs.' : isEs ? 'Efectivo Bs.' : 'Cash Bs.'
  if (m.includes('PAGO_MOVIL')) return isZh ? 'Pago Móvil' : isEs ? 'Pago Móvil' : 'Pago Móvil'
  if (m.includes('CARD_POS')) return isZh ? '刷卡 POS' : isEs ? 'Punto de Venta' : 'Card POS'
  if (m.includes('MIXTO') || m.includes('MIX')) return isZh ? '混合支付' : isEs ? 'Pago Mixto' : 'Mixed Pay'
  if (m.includes('ZELLE')) return 'Zelle'
  if (m.includes('TRANSFER')) return isZh ? '银行转账' : isEs ? 'Transferencia' : 'Transfer'
  return method
}

const todayStr = new Date().toLocaleDateString('en-CA')
const searchQuery = ref('')
const filterDate = ref(todayStr)

// 退货确认状态
const returnModalVisible = ref(false)
const targetReturnId = ref(null)

const filteredOrders = computed(() => {
  let result = props.orders
  if (searchQuery.value) {
    const q = searchQuery.value.toUpperCase()
    result = result.filter(o => (o.orderId && o.orderId.toUpperCase().includes(q)) || (o.clientName && o.clientName.toUpperCase().includes(q)))
  }
  if (filterDate.value) {
    result = result.filter(o => o.time && o.time.startsWith(filterDate.value))
  }
  return result
})

const openReturnModal = (dbId) => {
  targetReturnId.value = dbId
  returnModalVisible.value = true
}

const executeReturn = () => {
  if (targetReturnId.value) {
    emit('return', targetReturnId.value)
  }
  returnModalVisible.value = false
  targetReturnId.value = null
}
</script>