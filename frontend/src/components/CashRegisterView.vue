<!-- src/components/CashRegisterView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto">
    <!-- 顶部标题与日期筛选 -->
    <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-black text-slate-800 flex items-center gap-2">
          <span>📊</span> {{ tExt.title }}
        </h2>
        <p class="text-xs text-slate-500 mt-1 font-medium">{{ tExt.subtitle }}</p>
      </div>
      
      <div class="flex items-center gap-3">
        <span class="text-xs font-bold text-slate-600">{{ tExt.selectDate }}:</span>
        <input type="date" v-model="selectedDate" class="bg-white border border-slate-200 text-xs rounded-xl px-3 py-2 outline-none focus:border-blue-500 font-mono font-bold text-slate-700" />
        <button @click="selectedDate = todayStr" :class="selectedDate === todayStr ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'" class="px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer">
          {{ tExt.todayBtn }}
        </button>
        <button @click="selectedDate = ''" :class="selectedDate === '' ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'" class="px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer">
          {{ tExt.allBtn }}
        </button>
      </div>
    </div>

    <!-- 三个核心指标卡 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
      <div class="bg-gradient-to-br from-blue-600 to-indigo-700 p-6 rounded-2xl shadow-lg text-white space-y-2 relative overflow-hidden hover:scale-[1.01] transition-transform">
        <p class="text-xs font-bold text-blue-100 uppercase tracking-wider">{{ tExt.cardSelectedRevenue }}</p>
        <h3 class="text-3xl font-black font-mono">$ {{ formatNum(summary.selectedRevenue) }}</h3>
        <p class="text-xs text-blue-200 font-mono">= Bs. {{ formatNum(summary.selectedRevenue * bcvRate) }} (BCV)</p>
      </div>

      <div class="bg-gradient-to-br from-emerald-500 to-emerald-700 p-6 rounded-2xl shadow-lg text-white space-y-2 hover:scale-[1.01] transition-transform">
        <p class="text-xs font-bold text-emerald-100 uppercase tracking-wider">{{ tExt.cardTotalRevenue }}</p>
        <h3 class="text-3xl font-black font-mono">$ {{ formatNum(summary.totalRevenue) }}</h3>
        <p class="text-xs text-emerald-200 font-semibold">{{ tExt.totalOrders }}: {{ summary.totalOrders }} {{ tExt.unitOrder }}</p>
      </div>

      <div class="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-2xl shadow-lg text-white space-y-2 hover:scale-[1.01] transition-transform">
        <p class="text-xs font-bold text-slate-300 uppercase tracking-wider">{{ tExt.cardTotalQty }}</p>
        <h3 class="text-3xl font-black font-mono">{{ summary.totalQty }} <span class="text-sm font-sans">{{ tExt.unitItem }}</span></h3>
        <p class="text-xs text-slate-400 font-semibold">{{ tExt.stockStatus }}</p>
      </div>
    </div>

    <!-- 收款渠道拆分 -->
    <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg space-y-4">
      <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
        <span>💳</span> {{ tExt.paySplitTitle }}
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="bg-white border border-slate-200/80 p-4 rounded-xl space-y-1 shadow-2xs hover:border-blue-300 transition-colors">
          <span class="text-xs font-bold text-slate-500">💵 {{ tExt.payCashUSD }}</span>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ formatNum(paymentSplit.cashUsd) }}</div>
        </div>
        <div class="bg-white border border-slate-200/80 p-4 rounded-xl space-y-1 shadow-2xs hover:border-blue-300 transition-colors">
          <span class="text-xs font-bold text-slate-500">💳 {{ tExt.payZelle }}</span>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ formatNum(paymentSplit.zelle) }}</div>
        </div>
        <div class="bg-white border border-slate-200/80 p-4 rounded-xl space-y-1 shadow-2xs hover:border-blue-300 transition-colors">
          <span class="text-xs font-bold text-slate-500">⚡ {{ tExt.payPagoMovil }}</span>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ formatNum(paymentSplit.pagoMovil) }}</div>
        </div>
        <div class="bg-white border border-slate-200/80 p-4 rounded-xl space-y-1 shadow-2xs hover:border-blue-300 transition-colors">
          <span class="text-xs font-bold text-slate-500">🏦 {{ tExt.payTransfer }}</span>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ formatNum(paymentSplit.transferBs) }}</div>
        </div>
        <div class="bg-white border border-slate-200/80 p-4 rounded-xl space-y-1 shadow-2xs hover:border-blue-300 transition-colors">
          <span class="text-xs font-bold text-slate-500">🪙 {{ tExt.payUsdt }}</span>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ formatNum(paymentSplit.usdt) }}</div>
        </div>
      </div>
    </div>

    <!-- 历史交接班对账表 -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-lg overflow-hidden">
      <div class="p-6 border-b border-slate-200/60 flex items-center justify-between">
        <h3 class="font-bold text-slate-800 text-base">📋 {{ tExt.tableTitle }}</h3>
        <span class="text-xs text-slate-500 font-bold">{{ tExt.totalRecords }} {{ shiftRecords.length }} {{ tExt.unitRecord }}</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-6">{{ tExt.colTime }}</th>
              <th class="py-3.5 px-6">{{ tExt.colOperator }}</th>
              <th class="py-3.5 px-6">{{ tExt.colSystemCash }}</th>
              <th class="py-3.5 px-6">{{ tExt.colActualCash }}</th>
              <th class="py-3.5 px-6">{{ tExt.colZellePago }}</th>
              <th class="py-3.5 px-6">{{ tExt.colDiff }}</th>
              <th class="py-3.5 px-6">{{ tExt.colNotes }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="(r, i) in shiftRecords" :key="i" class="hover:bg-blue-50/30 transition-colors">
              <td class="py-4 px-6 font-mono text-xs text-slate-500">{{ r.closed_at }}</td>
              <td class="py-4 px-6 font-bold text-slate-800">{{ r.operator }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">$ {{ formatNum(r.system_cash_usd) }}</td>
              <td class="py-4 px-6 font-mono font-bold text-slate-900">$ {{ formatNum(r.actual_cash_usd) }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">
                <div class="text-[11px]">Zelle: ${{ formatNum(r.actual_zelle) }}</div>
                <div class="text-[11px]">Pago: Bs.{{ formatNum(r.actual_pago_movil) }}</div>
              </td>
              <td class="py-4 px-6">
                <!-- 🌟 盈亏差额高亮显示 -->
                <span 
                  class="px-2.5 py-1 rounded-md font-mono font-bold border text-xs" 
                  :class="(Number(r.actual_cash_usd || 0) - Number(r.system_cash_usd || 0)) >= 0 ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : 'text-rose-700 bg-rose-50 border-rose-200'"
                >
                  {{ (Number(r.actual_cash_usd || 0) - Number(r.system_cash_usd || 0)) >= 0 ? '+' : '' }}{{ formatNum(Number(r.actual_cash_usd || 0) - Number(r.system_cash_usd || 0)) }}
                </span>
              </td>
              <td class="py-4 px-6 text-xs text-slate-500 max-w-[150px] truncate" :title="r.notes">{{ r.notes || '-' }}</td>
            </tr>
            <tr v-if="shiftRecords.length === 0">
              <td colspan="7" class="py-16 text-center text-slate-400 text-xs font-bold">
                <span class="text-3xl block mb-2">📭</span>
                {{ tExt.emptyRecords }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from '../composables/useI18n'
import { useInventory } from '../composables/useInventory'
import { apiFetch } from '../utils/api'

const { currentLang } = useI18n()
const { bcvRate } = useInventory()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '销售概览与收银交接对账' : isEs ? 'Resumen de Ventas y Cierre de Caja' : 'Sales Overview & Shift Analytics',
    subtitle: isZh ? '实时监控每日营业额、多币种支付拆分及历史交接班盲盘审计' : isEs ? 'Monitoreo en tiempo real de ingresos diarios, desglose de pagos y auditoría de cierres.' : 'Real-time monitoring of daily revenue, payment split, and shift audit trails.',
    selectDate: isZh ? '选择日期' : isEs ? 'Seleccionar Fecha' : 'Select Date',
    todayBtn: isZh ? '今日' : isEs ? 'Hoy' : 'Today',
    allBtn: isZh ? '全部/今日' : isEs ? 'Todos' : 'All',
    cardSelectedRevenue: isZh ? '选中日期营业额' : isEs ? 'Ingresos del Día' : 'Revenue for Selected Date',
    cardTotalRevenue: isZh ? '历史总营业额' : isEs ? 'Ingresos Históricos Totales' : 'Total Historical Revenue',
    cardTotalQty: isZh ? '历史配件总销量' : isEs ? 'Total Repuestos Vendidos' : 'Total Parts Sold',
    totalOrders: isZh ? '总订单数' : isEs ? 'Total Pedidos' : 'Total Orders',
    unitOrder: isZh ? '单' : isEs ? 'pedidos' : 'orders',
    unitItem: isZh ? '件' : isEs ? 'ítems' : 'items',
    stockStatus: isZh ? '库存状态健康' : isEs ? 'Estado de inventario saludable' : 'Healthy stock status',
    paySplitTitle: isZh ? '多币种收款渠道拆分' : isEs ? 'Desglose de Canales de Pago' : 'Multi-Currency Payment Split',
    payCashUSD: isZh ? '美金现金' : isEs ? 'Efectivo USD' : 'Cash USD',
    payZelle: isZh ? 'Zelle' : isEs ? 'Zelle' : 'Zelle',
    payPagoMovil: isZh ? 'Pago Móvil' : isEs ? 'Pago Móvil' : 'Pago Móvil',
    payTransfer: isZh ? '转账 (Bs.)' : isEs ? 'Transferencia (Bs.)' : 'Transfer (Bs.)',
    payUsdt: isZh ? 'USDT' : isEs ? 'USDT' : 'USDT',
    tableTitle: isZh ? '历史交接班与盲盘点钞审计记录' : isEs ? 'Auditoría de Cierres de Caja' : 'Shift Handover Audit Logs',
    totalRecords: isZh ? '共' : isEs ? 'Total' : 'Total',
    unitRecord: isZh ? '班交接记录' : isEs ? 'registros' : 'records',
    colTime: isZh ? '交班时间' : isEs ? 'Hora de Cierre' : 'Closing Time',
    colOperator: isZh ? '收银员' : isEs ? 'Cajero' : 'Cashier',
    colSystemCash: isZh ? '系统现金应收' : isEs ? 'Efectivo Esperado' : 'System Cash Expected',
    colActualCash: isZh ? '实盘现金 (USD)' : isEs ? 'Efectivo Real (USD)' : 'Actual Cash (USD)',
    colZellePago: isZh ? 'ZELLE / PAGOMÓVIL' : isEs ? 'ZELLE / PAGOMÓVIL' : 'ZELLE / PAGO MÓVIL',
    colDiff: isZh ? '现金盈亏差额' : isEs ? 'Diferencia' : 'Difference',
    colNotes: isZh ? '盈亏备注' : isEs ? 'Notas' : 'Notes',
    emptyRecords: isZh ? '暂无历史交班归档记录' : isEs ? 'No hay registros de cierre de caja' : 'No shift handover records found'
  }
})

const todayStr = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Caracas' })
const selectedDate = ref(todayStr)

const shiftRecords = ref([])
const summary = ref({ selectedRevenue: 0, totalRevenue: 0, totalOrders: 0, totalQty: 0 })
const paymentSplit = ref({ cashUsd: 0, zelle: 0, pagoMovil: 0, transferBs: 0, usdt: 0 })

// 🌟 安全数字格式化
const formatNum = (val) => {
  const num = Number(val) || 0
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const fetchData = async () => {
  try {
    // 拉取交接班记录
    const res = await apiFetch('/api/pos/shift-records')
    if (res.ok) {
      shiftRecords.value = await res.json()
    }
    
    // 拉取销售订单并计算
    const posRes = await apiFetch('/api/pos/orders')
    if (posRes.ok) {
      const orders = await posRes.json()
      const activeOrders = orders.filter(o => o.status !== 'REFUNDED')
      
      let tRev = 0, tQty = 0, sRev = 0
      let pSplit = { cashUsd: 0, zelle: 0, pagoMovil: 0, transferBs: 0, usdt: 0 }
      
      activeOrders.forEach(o => {
        const isMatchDate = selectedDate.value ? (o.time && o.time.startsWith(selectedDate.value)) : true
        const rev = Number(o.totalUsd) || 0
        
        tRev += rev
        if (o.items && Array.isArray(o.items)) {
          o.items.forEach(item => tQty += (Number(item.quantity) || 0))
        }
        
        if (isMatchDate) {
          sRev += rev
          
          // 拆分支付方式（只统计选中日期的）
          const method = String(o.paymentMethod).toUpperCase()
          if (method.includes('CASH_USD')) pSplit.cashUsd += rev
          else if (method.includes('ZELLE')) pSplit.zelle += rev
          else if (method.includes('MOVIL')) pSplit.pagoMovil += rev
          else if (method.includes('TRANSFER')) pSplit.transferBs += rev
          else if (method.includes('USDT')) pSplit.usdt += rev
        }
      })
      
      // 🌟 修复：如果选的是“全部”，拆分和选中营业额都显示总计
      summary.value = {
        selectedRevenue: sRev,
        totalRevenue: tRev,
        totalOrders: activeOrders.length,
        totalQty: tQty
      }
      paymentSplit.value = pSplit
    }
  } catch (e) {
    console.error('获取收银数据失败:', e)
  }
}

watch(selectedDate, fetchData)
onMounted(fetchData)
</script>