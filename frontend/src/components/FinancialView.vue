<!-- src/components/FinancialView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部标题与导出按钮 -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">📊 财务利润中心</h2>
      
      <div class="flex items-center gap-3 flex-wrap">
        <!-- 🌟 自定义时间筛选器 -->
        <div class="relative">
          <div 
            @click="isDatePickerVisible = !isDatePickerVisible"
            class="flex items-center gap-2 bg-white border border-slate-200 hover:border-blue-300 rounded-xl px-4 py-2.5 cursor-pointer shadow-2xs transition-colors select-none"
          >
            <span class="text-sm font-bold font-mono text-blue-600">{{ startDate }}</span>
            <span class="text-slate-400 text-xs font-bold">至</span>
            <span class="text-sm font-bold font-mono text-blue-600">{{ endDate }}</span>
            <svg class="w-4 h-4 text-slate-400 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          </div>

          <!-- 日历面板 -->
          <div v-if="isDatePickerVisible" class="absolute top-full right-0 mt-2 bg-white/95 backdrop-blur-2xl border border-slate-200/80 rounded-2xl shadow-2xl z-50 p-4 w-72 animate-in fade-in slide-in-from-top-2">
            <!-- 头部：月份切换 -->
            <div class="flex items-center justify-between mb-4">
              <button @click.stop="changeMonth(-1)" class="p-1.5 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
              </button>
              <div class="font-black text-sm text-slate-800 font-mono">{{ currentYear }} 年 {{ currentMonth + 1 }} 月</div>
              <button @click.stop="changeMonth(1)" class="p-1.5 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
              </button>
            </div>

            <!-- 星期表头 -->
            <div class="grid grid-cols-7 gap-1 text-center mb-2">
              <div v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="text-[10px] font-bold text-slate-400">{{ day }}</div>
            </div>

            <!-- 日期格子 -->
            <div class="grid grid-cols-7 gap-1">
              <!-- 空白占位 -->
              <div v-for="n in firstDayOfWeek" :key="'empty-'+n" class="h-8"></div>
              <!-- 本月日期 -->
              <button 
                v-for="day in daysInMonth" 
                :key="day"
                @click.stop="handleDateClick(day)"
                :class="[
                  'h-8 rounded-lg text-xs font-bold transition-all flex items-center justify-center',
                  isSelected(day) ? 'bg-blue-600 text-white shadow-md' : 
                  isToday(day) ? 'text-blue-600 bg-blue-50' : 'text-slate-700 hover:bg-slate-100'
                ]"
              >
                {{ day }}
              </button>
            </div>

            <div class="mt-3 pt-3 border-t border-slate-100 flex justify-between">
              <button @click.stop="setThisMonth" class="text-xs font-bold text-blue-600 hover:underline">本月至今</button>
              <button @click.stop="isDatePickerVisible = false" class="text-xs font-bold text-slate-500 hover:text-slate-700">关闭</button>
            </div>
          </div>
        </div>

        <button 
          @click="exportProfitReport"
          class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20 transition-all cursor-pointer hover:scale-105"
        >
          📥 {{ tExt.exportBtn }}
        </button>
      </div>
    </div>

    <!-- 顶部核心指标卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="bg-white/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.revenue }}</p>
        <h3 class="text-2xl font-black text-blue-600 font-mono">$ {{ analytics.total_revenue_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_revenue_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.cost }}</p>
        <h3 class="text-2xl font-black text-slate-700 font-mono">$ {{ analytics.total_cost_usd.toFixed(2) }}</h3>
        <p class="text-xs text-slate-400 font-mono">Bs. {{ (analytics.total_cost_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-white/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.expenses }}</p>
        <h3 class="text-2xl font-black text-rose-500 font-mono">$ {{ analytics.total_expenses_usd.toFixed(2) }}</h3>
        <p class="text-xs text-rose-400 font-mono font-bold">Bs. {{ (analytics.total_expenses_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <!-- 🌟 应收欠款（不随时间过滤） -->
      <div class="bg-amber-50/80 backdrop-blur-xl p-5 rounded-2xl border border-amber-200 shadow-lg space-y-2">
        <p class="text-xs font-bold text-amber-600 uppercase tracking-wider">{{ tExt.debt }}</p>
        <h3 class="text-2xl font-black text-amber-700 font-mono">$ {{ analytics.total_debt_usd.toFixed(2) }}</h3>
        <p class="text-xs text-amber-600 font-mono font-bold">Bs. {{ (analytics.total_debt_usd * bcvRate).toFixed(2) }}</p>
      </div>

      <div class="bg-emerald-50/80 backdrop-blur-xl p-5 rounded-2xl border border-emerald-300 shadow-lg space-y-2 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-bl-full"></div>
        <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider">{{ tExt.netProfit }}</p>
        <h3 class="text-2xl font-black text-emerald-700 font-mono">$ {{ analytics.net_profit_usd.toFixed(2) }}</h3>
        <p class="text-xs text-emerald-600 font-mono font-bold">Bs. {{ (analytics.net_profit_usd * bcvRate).toFixed(2) }}</p>
      </div>
    </div>

    <!-- 收银对账分类 -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl p-6 space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
          💳 {{ tExt.paymentBreakdown }}
        </h3>
        <span class="text-xs bg-blue-500/10 text-blue-700 border border-blue-200/60 px-3 py-1 rounded-xl font-mono font-bold shadow-2xs">
          BCV: {{ bcvRate }}
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>💳 Card POS</span>
            <span class="text-blue-600 font-mono">{{ paymentBreakdown.cardPos.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cardPos.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>⚡ Pago Móvil</span>
            <span class="text-indigo-600 font-mono">{{ paymentBreakdown.pagoMovil.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.pagoMovil.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>🇻🇪 Cash Bs.</span>
            <span class="text-emerald-600 font-mono">{{ paymentBreakdown.cashBs.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cashBs.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>💵 Cash USD</span>
            <span class="text-emerald-600 font-mono">{{ paymentBreakdown.cashUSD.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.cashUSD.totalUSD.toFixed(2) }}</div>
        </div>
        <div class="bg-white/70 hover:bg-white backdrop-blur-md border border-white/90 hover:border-blue-300 rounded-2xl p-4 space-y-1 shadow-2xs transition-all duration-200 hover:scale-[1.02]">
          <div class="flex items-center justify-between text-xs font-bold text-slate-500">
            <span>🔄 Pago Mixto</span>
            <span class="text-purple-600 font-mono">{{ paymentBreakdown.pagoMixto.count }} {{ tExt.unit }}</span>
          </div>
          <div class="text-lg font-black text-slate-900 font-mono">$ {{ paymentBreakdown.pagoMixto.totalUSD.toFixed(2) }}</div>
        </div>
      </div>
    </div>

    <!-- 每日利润对账流水 -->
    <div class="bg-white/75 backdrop-blur-xl rounded-2xl border border-white/80 shadow-xl overflow-hidden">
      <div class="p-6 border-b border-slate-200/60 flex items-center justify-between bg-white/40 backdrop-blur-md">
        <div>
          <h3 class="font-bold text-slate-800 text-base">📈 {{ tExt.dailyAuditTitle }}</h3>
          <p class="text-xs text-slate-400 mt-0.5 font-medium">{{ startDate }} {{ tExt.to }} {{ endDate }} {{ tExt.auditSubtitle }}</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[850px]">
          <thead>
            <tr class="bg-white/60 backdrop-blur-md border-b border-slate-200/60 text-xs font-black text-slate-600 uppercase tracking-wider">
              <th class="py-3.5 px-6">{{ tExt.orderNo }}</th>
              <th class="py-3.5 px-6">{{ tExt.time }}</th>
              <th class="py-3.5 px-6">{{ tExt.payMethod }}</th>
              <th class="py-3.5 px-6">{{ tExt.revenueUsd }}</th>
              <th class="py-3.5 px-6">{{ tExt.revenueVes }}</th>
              <th class="py-3.5 px-6">{{ tExt.costUsd }}</th>
              <th class="py-3.5 px-6">{{ tExt.realProfit }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200/60 text-sm font-medium">
            <tr v-for="row in dailyAuditList" :key="row.id" class="hover:bg-blue-500/10 transition-all duration-200 cursor-pointer">
              <td class="py-3.5 px-6 font-mono font-black text-blue-600">#{{ row.id }}</td>
              <td class="py-3.5 px-6 text-xs text-slate-500 font-mono">{{ row.date }}</td>
              <td class="py-3.5 px-6">
                <span class="bg-blue-500/15 text-blue-700 border border-blue-200/60 px-2.5 py-1 rounded-lg text-xs font-bold font-mono shadow-2xs">
                  {{ row.payment_method }}
                </span>
              </td>
              <td class="py-3.5 px-6 font-mono font-black text-slate-900">$ {{ Number(row.revenue_usd || 0).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-600 font-bold">Bs. {{ (Number(row.revenue_usd || 0) * bcvRate).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-500 font-bold">$ {{ Number(row.cost_usd || 0).toFixed(2) }}</td>
              <td class="py-3.5 px-6 font-mono font-black text-emerald-600">
                $ {{ Number(row.profit_usd || 0).toFixed(2) }}
                <span class="block text-[11px] text-emerald-700/80 font-normal">
                  Bs. {{ (Number(row.profit_usd || 0) * bcvRate).toFixed(2) }}
                </span>
              </td>
            </tr>
            <tr v-if="dailyAuditList.length === 0">
              <td colspan="7" class="py-16 text-center text-slate-400 text-xs font-bold">{{ tExt.noData }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'

const { t, currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  
  if (isZh) {
    return {
      exportBtn: '导出利润报表',
      revenue: '总营业收入',
      cost: '总进货成本',
      expenses: '日常开支 (Expenses)',
      debt: '客户应收欠款 (Fiado)',
      netProfit: '净利润',
      paymentBreakdown: '收银对账分类 (基于所选时间段)',
      unit: '笔',
      dailyAuditTitle: '每日利润对账流水',
      auditSubtitle: '的真实毛利贡献',
      orderNo: '单据编号',
      time: '交易时间',
      payMethod: '支付方式',
      revenueUsd: '营业额 (USD)',
      revenueVes: '折算收入 (VES)',
      costUsd: '进货成本 (USD)',
      realProfit: '真实毛利',
      noData: '该时间段内暂无交易流水',
      
      // 导出报表用
      exportTitle: 'TOSTIKYK ERP - 财务利润综合报表',
      to: '至',
      rateLabel: '当前 BCV 汇率',
      coreMetrics: '【核心财务指标 (USD / VES)】',
      dailyDetails: '【每日利润对账流水明细】',
      profitUsd: '真实毛利(USD)',
      profitBs: '真实毛利(Bs.)'
    }
  } else if (isEs) {
    return {
      exportBtn: 'Exportar Reporte',
      revenue: 'Ingresos Totales',
      cost: 'Costo Total',
      expenses: 'Gastos Diarios',
      debt: 'Cuentas por Cobrar (Fiado)',
      netProfit: 'Utilidad Neta',
      paymentBreakdown: 'Conciliación de Caja (Período)',
      unit: 'trans.',
      dailyAuditTitle: 'Auditoría Diaria de Ganancias',
      auditSubtitle: 'contribución real a la ganancia bruta',
      orderNo: 'Nro. Orden',
      time: 'Fecha',
      payMethod: 'Método de Pago',
      revenueUsd: 'Ingresos (USD)',
      revenueVes: 'Ingresos (VES)',
      costUsd: 'Costo (USD)',
      realProfit: 'Ganancia Real',
      noData: 'Sin transacciones en este período',
      
      exportTitle: 'TOSTIKYK ERP - Informe de Ganancias',
      to: 'a',
      rateLabel: 'Tasa BCV Actual',
      coreMetrics: '【Indicadores Financieros Principales】',
      dailyDetails: '【Detalle Diario de Ganancias】',
      profitUsd: 'Ganancia Real (USD)',
      profitBs: 'Ganancia Real (Bs.)'
    }
  } else {
    return {
      exportBtn: 'Export Report',
      revenue: 'Total Revenue',
      cost: 'Total Cost',
      expenses: 'Daily Expenses',
      debt: 'Accounts Receivable (Fiado)',
      netProfit: 'Net Profit',
      paymentBreakdown: 'Payment Breakdown (Period)',
      unit: 'txns',
      dailyAuditTitle: 'Daily Profit Audit Trail',
      auditSubtitle: 'real gross profit contribution',
      orderNo: 'Order No.',
      time: 'Date',
      payMethod: 'Payment Method',
      revenueUsd: 'Revenue (USD)',
      revenueVes: 'Revenue (VES)',
      costUsd: 'Cost (USD)',
      realProfit: 'Real Profit',
      noData: 'No transactions in this period',
      
      exportTitle: 'TOSTIKYK ERP - Financial Profit Report',
      to: 'to',
      rateLabel: 'Current BCV Rate',
      coreMetrics: '[ Key Financial Indicators ]',
      dailyDetails: '[ Daily Profit Audit Trail ]',
      profitUsd: 'Real Profit (USD)',
      profitBs: 'Real Profit (Bs.)'
    }
  }
})

const bcvRate = ref(36.50)
const analytics = ref({
  total_revenue_usd: 0,
  total_cost_usd: 0,
  total_expenses_usd: 0,
  total_debt_usd: 0,
  net_profit_usd: 0
})

const paymentBreakdown = ref({
  cardPos: { count: 0, totalUSD: 0 },
  pagoMovil: { count: 0, totalUSD: 0 },
  cashBs: { count: 0, totalUSD: 0 },
  cashUSD: { count: 0, totalUSD: 0 },
  pagoMixto: { count: 0, totalUSD: 0 }
})

const rawOrders = ref([])
const rawExpenses = ref([])
const fixedDebt = ref(0)

const now = new Date()
const defaultStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0]
const defaultEnd = now.toISOString().split('T')[0]
const startDate = ref(defaultStart)
const endDate = ref(defaultEnd)

// 自定义日历状态
const isDatePickerVisible = ref(false)
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth())
const selectingStartDate = ref(true)

const firstDayOfWeek = computed(() => new Date(currentYear.value, currentMonth.value, 1).getDay())
const daysInMonth = computed(() => new Date(currentYear.value, currentMonth.value + 1, 0).getDate())

const changeMonth = (offset) => {
  const newDate = new Date(currentYear.value, currentMonth.value + offset, 1)
  currentYear.value = newDate.getFullYear()
  currentMonth.value = newDate.getMonth()
}

const handleDateClick = (day) => {
  const formattedDate = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  
  if (selectingStartDate.value) {
    startDate.value = formattedDate
    if (endDate.value < startDate.value) endDate.value = formattedDate
    selectingStartDate.value = false
  } else {
    endDate.value = formattedDate
    selectingStartDate.value = true
    isDatePickerVisible.value = false
  }
}

const isSelected = (day) => {
  const d = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  return d === startDate.value || d === endDate.value
}

const isToday = (day) => {
  const today = new Date().toISOString().split('T')[0]
  const d = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  return d === today
}

const setThisMonth = () => {
  startDate.value = defaultStart
  endDate.value = defaultEnd
  selectingStartDate.value = true
  isDatePickerVisible.value = false
}

const dailyAuditList = computed(() => {
  const filtered = rawOrders.value.filter(o => {
    if (o.status === 'REFUNDED') return false
    const dateStr = (o.time || o.created_at || '').substring(0, 10)
    return dateStr >= startDate.value && dateStr <= endDate.value
  })

  let cpCount = 0, cpSum = 0
  let pmCount = 0, pmSum = 0
  let cbCount = 0, cbSum = 0
  let cuCount = 0, cuSum = 0
  let mixCount = 0, mixSum = 0

  let totalRev = 0
  let totalCost = 0

  const list = filtered.map(order => {
    const rev = Number(order.totalUsd || 0)
    let orderCost = 0
    if (order.items && order.items.length > 0) {
      order.items.forEach(item => {
        orderCost += (Number(item.cost_price || 0) * Number(item.quantity || 0))
      })
    }
    const profit = rev - orderCost
    totalRev += rev
    totalCost += orderCost

    const method = String(order.paymentMethod || 'Cash_USD').trim()
    const mUpper = method.toUpperCase()

    if (mUpper.includes('CARD_POS')) { cpCount++; cpSum += rev; }
    else if (mUpper.includes('PAGO_MOVIL')) { pmCount++; pmSum += rev; }
    else if (mUpper.includes('CASH_BS')) { cbCount++; cbSum += rev; }
    else if (mUpper.includes('CASH_USD')) { cuCount++; cuSum += rev; }
    else if (mUpper.includes('MIXTO') || mUpper.includes('MIX')) { mixCount++; mixSum += rev; }
    else { cuCount++; cuSum += rev; }

    return {
      id: order.orderId || order.dbId,
      date: order.time || order.created_at || 'Just now',
      payment_method: method,
      revenue_usd: rev,
      cost_usd: orderCost,
      profit_usd: profit
    }
  })

  paymentBreakdown.value = {
    cardPos: { count: cpCount, totalUSD: cpSum },
    pagoMovil: { count: pmCount, totalUSD: pmSum },
    cashBs: { count: cbCount, totalUSD: cbSum },
    cashUSD: { count: cuCount, totalUSD: cuSum },
    pagoMixto: { count: mixCount, totalUSD: mixSum }
  }

  let totalExpenses = 0
  rawExpenses.value.forEach(e => {
    const eDate = e.expense_date || ''
    if (eDate >= startDate.value && eDate <= endDate.value) {
      const usdVal = e.currency === 'USD' ? Number(e.amount) : Number(e.amount) / Number(e.exchange_rate || 1)
      totalExpenses += usdVal
    }
  })

  analytics.value = {
    total_revenue_usd: totalRev,
    total_cost_usd: totalCost,
    total_expenses_usd: totalExpenses,
    total_debt_usd: fixedDebt.value,
    net_profit_usd: totalRev - totalCost - totalExpenses
  }

  return list
})

const fetchFinancialData = async () => {
  try {
    const rateRes = await apiFetch('/api/settings/bcv-rate')
    if (rateRes.ok) {
      const rateData = await rateRes.json()
      bcvRate.value = rateData.rate || 36.50
    }

    const orderRes = await apiFetch('/api/pos/orders')
    if (orderRes.ok) {
      rawOrders.value = await orderRes.json()
    }

    const expRes = await apiFetch('/api/expenses')
    if (expRes.ok) {
      rawExpenses.value = await expRes.json()
    }

    const debtRes = await apiFetch('/api/clients/analytics/debt-summary')
    if (debtRes.ok) {
      const debtData = await debtRes.json()
      fixedDebt.value = debtData.total_debt_usd || 0
    }

  } catch (e) {
    console.error("加载财务对账数据失败:", e)
  }
}

const exportProfitReport = () => {
  const t = tExt.value
  const bcv = bcvRate.value

  let csvContent = "\uFEFF"
  csvContent += `${t.exportTitle} (${startDate.value} ${t.to} ${endDate.value})\n`
  csvContent += `${t.rateLabel},${bcv}\n\n`

  csvContent += `${t.coreMetrics}\n`
  csvContent += `${t.revenue},$ ${analytics.value.total_revenue_usd.toFixed(2)},Bs. ${(analytics.value.total_revenue_usd * bcv).toFixed(2)}\n`
  csvContent += `${t.cost},$ ${analytics.value.total_cost_usd.toFixed(2)},Bs. ${(analytics.value.total_cost_usd * bcv).toFixed(2)}\n`
  csvContent += `${t.expenses},$ ${analytics.value.total_expenses_usd.toFixed(2)},Bs. ${(analytics.value.total_expenses_usd * bcv).toFixed(2)}\n`
  csvContent += `${t.debt},$ ${analytics.value.total_debt_usd.toFixed(2)},Bs. ${(analytics.value.total_debt_usd * bcv).toFixed(2)}\n`
  csvContent += `${t.netProfit},$ ${analytics.value.net_profit_usd.toFixed(2)},Bs. ${(analytics.value.net_profit_usd * bcv).toFixed(2)}\n\n`

  csvContent += `${t.dailyDetails}\n`
  csvContent += `${t.orderNo},${t.time},${t.payMethod},${t.revenueUsd},${t.revenueVes},${t.costUsd},${t.profitUsd},${t.profitBs}\n`
  
  dailyAuditList.value.forEach(row => {
    const safeMethod = `"${row.payment_method}"` 
    csvContent += `${row.id},${row.date},${safeMethod},${Number(row.revenue_usd).toFixed(2)},${(Number(row.revenue_usd) * bcv).toFixed(2)},${Number(row.cost_usd).toFixed(2)},${Number(row.profit_usd).toFixed(2)},${(Number(row.profit_usd) * bcv).toFixed(2)}\n`
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = `TOSTIKYK_Profit_${startDate.value}_to_${endDate.value}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const handleClickOutside = (e) => {
  const picker = document.querySelector('.absolute.top-full.right-0')
  if (isDatePickerVisible.value && picker && !picker.contains(e.target) && !e.target.closest('.relative')) {
    isDatePickerVisible.value = false
  }
}

onMounted(() => {
  fetchFinancialData()
  window.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>