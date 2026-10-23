<!-- src/components/FinancialView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部标题与导出按钮 -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <h2 class="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
        <span>📊</span> {{ tExt.title }}
      </h2>
      
      <div class="flex items-center gap-3 flex-wrap">
        <!-- 自定义时间筛选器 -->
        <div class="relative">
          <div 
            @click="isDatePickerVisible = !isDatePickerVisible"
            class="flex items-center gap-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-blue-400 dark:hover:border-blue-500 rounded-xl px-4 py-2.5 cursor-pointer shadow-2xs hover:shadow-md transition-all select-none"
          >
            <span class="text-sm font-bold font-mono text-blue-600 dark:text-blue-400">{{ startDate }}</span>
            <span class="text-slate-400 dark:text-slate-500 text-xs font-bold">{{ tExt.to }}</span>
            <span class="text-sm font-bold font-mono text-blue-600 dark:text-blue-400">{{ endDate }}</span>
            <svg class="w-4 h-4 text-slate-400 dark:text-slate-500 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          </div>

          <!-- 日历面板 -->
          <div v-if="isDatePickerVisible" class="absolute top-full right-0 mt-2 bg-white/95 dark:bg-slate-800/95 backdrop-blur-2xl border border-slate-200/80 dark:border-slate-700 rounded-2xl shadow-2xl z-50 p-4 w-72 animate-in fade-in slide-in-from-top-2">
            <div class="flex items-center justify-between mb-4">
              <button @click.stop="changeMonth(-1)" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg text-slate-500 dark:text-slate-400 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
              </button>
              <div class="font-black text-sm text-slate-800 dark:text-slate-200 font-mono">{{ currentYear }} {{ tExt.yearUnit }} {{ currentMonth + 1 }} {{ tExt.monthUnit }}</div>
              <button @click.stop="changeMonth(1)" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg text-slate-500 dark:text-slate-400 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
              </button>
            </div>

            <div class="grid grid-cols-7 gap-1 text-center mb-2">
              <div v-for="day in tExt.weekDays" :key="day" class="text-[10px] font-bold text-slate-400 dark:text-slate-500">{{ day }}</div>
            </div>

            <div class="grid grid-cols-7 gap-1">
              <div v-for="n in firstDayOfWeek" :key="'empty-'+n" class="h-8"></div>
              <button 
                v-for="day in daysInMonth" 
                :key="day"
                @click.stop="handleDateClick(day)"
                :class="[
                  'h-8 rounded-lg text-xs font-bold transition-all flex items-center justify-center',
                  isSelected(day) ? 'bg-blue-600 text-white shadow-md' : 
                  isToday(day) ? 'text-blue-600 bg-blue-50 dark:bg-blue-900/30 dark:text-blue-400' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                ]"
              >
                {{ day }}
              </button>
            </div>

            <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700 flex justify-between">
              <button @click.stop="setThisMonth" class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">{{ tExt.thisMonth }}</button>
              <button @click.stop="isDatePickerVisible = false" class="text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200">{{ tExt.close }}</button>
            </div>
          </div>
        </div>

        <button 
          @click="exportProfitReport"
          class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20 hover:shadow-lg hover:shadow-emerald-500/30 transition-all cursor-pointer hover:-translate-y-0.5"
        >
          📥 {{ tExt.exportBtn }}
        </button>
      </div>
    </div>

    <!-- 🌟 顶部核心指标卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <!-- 营收 -->
      <div class="bg-white/75 dark:bg-slate-800/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 dark:border-slate-700 shadow-lg space-y-2 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 hover:bg-white dark:hover:bg-slate-800 hover:border-blue-200 dark:hover:border-blue-500 cursor-default">
        <p class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ tExt.revenue }}</p>
        <h3 class="text-2xl font-black text-blue-600 dark:text-blue-400 font-mono">$ {{ formatNum(analytics.total_revenue_usd) }}</h3>
        <p class="text-xs text-slate-400 dark:text-slate-500 font-mono">Bs. {{ formatNum(analytics.total_revenue_usd * bcvRate) }}</p>
      </div>

      <!-- 成本 -->
      <div class="bg-white/75 dark:bg-slate-800/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 dark:border-slate-700 shadow-lg space-y-2 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 hover:bg-white dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-500 cursor-default">
        <p class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ tExt.cost }}</p>
        <h3 class="text-2xl font-black text-slate-700 dark:text-slate-200 font-mono">$ {{ formatNum(analytics.total_cost_usd) }}</h3>
        <p class="text-xs text-slate-400 dark:text-slate-500 font-mono">Bs. {{ formatNum(analytics.total_cost_usd * bcvRate) }}</p>
      </div>

      <!-- 开支 -->
      <div class="bg-white/75 dark:bg-slate-800/75 backdrop-blur-xl p-5 rounded-2xl border border-white/80 dark:border-slate-700 shadow-lg space-y-2 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 hover:bg-white dark:hover:bg-slate-800 hover:border-rose-200 dark:hover:border-rose-500 cursor-default">
        <p class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ tExt.expenses }}</p>
        <h3 class="text-2xl font-black text-rose-500 dark:text-rose-400 font-mono">$ {{ formatNum(analytics.total_expenses_usd) }}</h3>
        <p class="text-xs text-rose-400 dark:text-rose-500 font-mono font-bold">Bs. {{ formatNum(analytics.total_expenses_usd * bcvRate) }}</p>
      </div>

      <!-- 欠款 -->
      <div class="bg-amber-50/80 dark:bg-amber-900/20 backdrop-blur-xl p-5 rounded-2xl border border-amber-200 dark:border-amber-700/50 shadow-lg space-y-2 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 hover:bg-amber-100/90 dark:hover:bg-amber-900/40 hover:border-amber-300 dark:hover:border-amber-600 cursor-default">
        <p class="text-xs font-bold text-amber-600 dark:text-amber-500 uppercase tracking-wider">{{ tExt.debt }}</p>
        <h3 class="text-2xl font-black text-amber-700 dark:text-amber-400 font-mono">$ {{ formatNum(analytics.total_debt_usd) }}</h3>
        <p class="text-xs text-amber-600 dark:text-amber-500 font-mono font-bold">Bs. {{ formatNum(analytics.total_debt_usd * bcvRate) }}</p>
      </div>

      <!-- 净利润 -->
      <div class="bg-emerald-50/80 dark:bg-emerald-900/20 backdrop-blur-xl p-5 rounded-2xl border border-emerald-300 dark:border-emerald-700/50 shadow-lg space-y-2 relative overflow-hidden transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 hover:bg-emerald-100/90 dark:hover:bg-emerald-900/40 hover:border-emerald-400 dark:hover:border-emerald-600 cursor-default">
        <div class="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-bl-full"></div>
        <p class="text-xs font-bold text-emerald-600 dark:text-emerald-500 uppercase tracking-wider">{{ tExt.netProfit }}</p>
        <h3 class="text-2xl font-black text-emerald-700 dark:text-emerald-400 font-mono">$ {{ formatNum(analytics.net_profit_usd) }}</h3>
        <p class="text-xs text-emerald-600 dark:text-emerald-500 font-mono font-bold">Bs. {{ formatNum(analytics.net_profit_usd * bcvRate) }}</p>
      </div>
    </div>

    <!-- 🌟 可视化图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 营收与利润趋势图 -->
      <div class="bg-white/75 dark:bg-slate-800/75 backdrop-blur-xl rounded-2xl border border-white/80 dark:border-slate-700 shadow-xl p-6 transition-shadow duration-300 hover:shadow-2xl">
        <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base mb-4 flex items-center gap-2">
          <span>📈</span> {{ tExt.chartTrendTitle }}
        </h3>
        <div ref="trendChartRef" class="w-full h-72"></div>
      </div>

      <!-- 支付渠道占比图 -->
      <div class="bg-white/75 dark:bg-slate-800/75 backdrop-blur-xl rounded-2xl border border-white/80 dark:border-slate-700 shadow-xl p-6 transition-shadow duration-300 hover:shadow-2xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base flex items-center gap-2">
            <span>💳</span> {{ tExt.paymentBreakdown }}
          </h3>
          <span class="text-xs bg-blue-500/10 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-200/60 dark:border-blue-500/30 px-3 py-1 rounded-xl font-mono font-bold shadow-2xs">
            BCV: {{ bcvRate }}
          </span>
        </div>
        <div ref="pieChartRef" class="w-full h-72"></div>
      </div>
    </div>

    <!-- 🌟 每日利润对账流水 -->
    <div class="bg-white/75 dark:bg-slate-800/75 backdrop-blur-xl rounded-2xl border border-white/80 dark:border-slate-700 shadow-xl overflow-hidden">
      <div class="p-6 border-b border-slate-200/60 dark:border-slate-700 flex items-center justify-between bg-white/40 dark:bg-slate-800/40 backdrop-blur-md">
        <div>
          <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base">📋 {{ tExt.dailyAuditTitle }}</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">{{ startDate }} {{ tExt.to }} {{ endDate }} {{ tExt.auditSubtitle }}</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[850px]">
          <thead>
            <tr class="bg-white/60 dark:bg-slate-800/60 backdrop-blur-md border-b border-slate-200/60 dark:border-slate-700 text-xs font-black text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              <th class="py-3.5 px-6">{{ tExt.orderNo }}</th>
              <th class="py-3.5 px-6">{{ tExt.time }}</th>
              <th class="py-3.5 px-6">{{ tExt.payMethod }}</th>
              <th class="py-3.5 px-6">{{ tExt.revenueUsd }}</th>
              <th class="py-3.5 px-6">{{ tExt.revenueVes }}</th>
              <th class="py-3.5 px-6">{{ tExt.costUsd }}</th>
              <th class="py-3.5 px-6">{{ tExt.realProfit }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200/60 dark:divide-slate-700/60 text-sm font-medium">
            <tr 
              v-for="row in dailyAuditList" 
              :key="row.id" 
              class="hover:bg-blue-50/60 dark:hover:bg-blue-900/20 transition-all duration-200 cursor-pointer group border-l-4 border-transparent hover:border-blue-500"
            >
              <td class="py-3.5 px-6 font-mono font-black text-blue-600 dark:text-blue-400 group-hover:scale-110 group-hover:origin-left transition-transform">
                #{{ row.id }}
              </td>
              <td class="py-3.5 px-6 text-xs text-slate-500 dark:text-slate-400 font-mono">{{ row.date }}</td>
              <td class="py-3.5 px-6">
                <span class="bg-blue-500/10 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-200/60 dark:border-blue-500/30 px-2.5 py-1 rounded-lg text-xs font-bold font-mono shadow-2xs group-hover:bg-blue-600 dark:group-hover:bg-blue-500 group-hover:text-white transition-colors">
                  {{ getPaymentMethodLabel(row.payment_method) }}
                </span>
              </td>
              <td class="py-3.5 px-6 font-mono font-black text-slate-900 dark:text-slate-100">$ {{ formatNum(row.revenue_usd) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-600 dark:text-slate-300 font-bold group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">Bs. {{ formatNum(row.revenue_usd * bcvRate) }}</td>
              <td class="py-3.5 px-6 font-mono text-slate-500 dark:text-slate-400 font-bold">$ {{ formatNum(row.cost_usd) }}</td>
              <td class="py-3.5 px-6 font-mono font-black text-emerald-600 dark:text-emerald-400 group-hover:text-emerald-700 dark:group-hover:text-emerald-300 transition-colors">
                $ {{ formatNum(row.profit_usd) }}
                <span class="block text-[11px] text-emerald-700/80 dark:text-emerald-500/80 font-normal">
                  Bs. {{ formatNum(row.profit_usd * bcvRate) }}
                </span>
              </td>
            </tr>
            <tr v-if="dailyAuditList.length === 0">
              <td colspan="7" class="py-16 text-center text-slate-400 dark:text-slate-500 text-xs font-bold">{{ tExt.noData }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'

// 🌟 按需引入 ECharts 核心模块
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { LabelLayout, UniversalTransition } from 'echarts/features'
import { CanvasRenderer } from 'echarts/renderers'

import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme' // 🌟 引入主题
import { apiFetch } from '../utils/api'

const { t, currentLang } = useI18n()
const { isDark } = useTheme() // 🌟 获取当前主题状态

echarts.use([
  BarChart, LineChart, PieChart, TitleComponent, TooltipComponent,
  GridComponent, LegendComponent, LabelLayout, UniversalTransition, CanvasRenderer
])

const formatNum = (val) => {
  const num = Number(val) || 0
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// ... (tExt 和之前一模一样，这里为了篇幅省略，直接照搬你原来的 tExt 即可)
const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '财务利润中心' : isEs ? 'Centro de Ganancias' : 'Profit Center',
    exportBtn: isZh ? '导出利润报表' : isEs ? 'Exportar Reporte' : 'Export Report',
    revenue: isZh ? '总营业收入' : isEs ? 'Ingresos Totales' : 'Total Revenue',
    cost: isZh ? '总进货成本' : isEs ? 'Costo Total' : 'Total Cost',
    expenses: isZh ? '日常开支' : isEs ? 'Gastos Diarios' : 'Daily Expenses',
    debt: isZh ? '客户应收欠款' : isEs ? 'Cuentas por Cobrar' : 'Accounts Receivable',
    netProfit: isZh ? '净利润' : isEs ? 'Utilidad Neta' : 'Net Profit',
    paymentBreakdown: isZh ? '支付渠道占比' : isEs ? 'Distribución de Pagos' : 'Payment Breakdown',
    chartTrendTitle: isZh ? '营收与利润趋势' : isEs ? 'Tendencia de Ingresos y Ganancias' : 'Revenue & Profit Trend',
    dailyAuditTitle: isZh ? '每日利润对账流水' : isEs ? 'Auditoría Diaria de Ganancias' : 'Daily Profit Audit',
    auditSubtitle: isZh ? '的真实毛利贡献' : isEs ? 'contribución real' : 'real gross profit contribution',
    orderNo: isZh ? '单据编号' : isEs ? 'Nro. Orden' : 'Order No.',
    time: isZh ? '交易时间' : isEs ? 'Fecha' : 'Date',
    payMethod: isZh ? '支付方式' : isEs ? 'Método de Pago' : 'Payment Method',
    revenueUsd: isZh ? '营业额 (USD)' : isEs ? 'Ingresos (USD)' : 'Revenue (USD)',
    revenueVes: isZh ? '折算收入 (VES)' : isEs ? 'Ingresos (VES)' : 'Revenue (VES)',
    costUsd: isZh ? '进货成本 (USD)' : isEs ? 'Costo (USD)' : 'Cost (USD)',
    realProfit: isZh ? '真实毛利' : isEs ? 'Ganancia Real' : 'Real Profit',
    noData: isZh ? '该时间段内暂无交易流水' : isEs ? 'Sin transacciones en este período' : 'No transactions found',
    to: isZh ? '至' : isEs ? 'a' : 'to',
    close: isZh ? '关闭' : isEs ? 'Cerrar' : 'Close',
    thisMonth: isZh ? '本月至今' : isEs ? 'Este mes' : 'This month',
    yearUnit: isZh ? '年' : isEs ? '' : '',
    monthUnit: isZh ? '月' : isEs ? '' : '',
    weekDays: isZh ? ['日', '一', '二', '三', '四', '五', '六'] : isEs ? ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'] : ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
    chartRevenue: isZh ? '营收' : isEs ? 'Ingresos' : 'Revenue',
    chartProfit: isZh ? '毛利' : isEs ? 'Ganancia Bruta' : 'Gross Profit',
    chartAmount: isZh ? '金额 (USD)' : isEs ? 'Monto (USD)' : 'Amount (USD)',
    chartOther: isZh ? '其他' : isEs ? 'Otros' : 'Other',
    emptyData: isZh ? '暂无数据' : isEs ? 'Sin datos' : 'No data',
    exportTitle: isZh ? '财务利润综合报表' : isEs ? 'Informe de Ganancias' : 'Financial Profit Report',
    rateLabel: isZh ? '当前 BCV 汇率' : isEs ? 'Tasa BCV Actual' : 'Current BCV Rate',
    coreMetrics: isZh ? '【核心财务指标】' : isEs ? '【Indicadores Financieros】' : '[ Key Financial Indicators ]',
    dailyDetails: isZh ? '【每日利润对账流水明细】' : isEs ? '【Detalle Diario de Ganancias】' : '[ Daily Profit Audit Trail ]',
    profitUsd: isZh ? '真实毛利(USD)' : isEs ? 'Ganancia (USD)' : 'Real Profit (USD)',
    profitBs: isZh ? '真实毛利(Bs.)' : isEs ? 'Ganancia (Bs.)' : 'Real Profit (Bs.)'
  }
})

const getPaymentMethodLabel = (methodCode) => {
  if (!methodCode) return '-'
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  const m = String(methodCode).toUpperCase()

  if (m.includes('CARD_POS')) return isZh ? '刷卡 (POS)' : isEs ? 'Punto de Venta' : 'Card POS'
  if (m.includes('PAGO_MOVIL')) return isZh ? 'Pago Móvil' : isEs ? 'Pago Móvil' : 'Pago Móvil'
  if (m.includes('CASH_BS')) return isZh ? '现金 (Bs.)' : isEs ? 'Efectivo Bs.' : 'Cash Bs.'
  if (m.includes('CASH_USD')) return isZh ? '现金 (美元)' : isEs ? 'Efectivo USD' : 'Cash USD'
  if (m.includes('MIXTO') || m.includes('MIX')) return isZh ? '混合支付' : isEs ? 'Pago Mixto' : 'Mixed Pay'
  return methodCode
}

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

// ==================== ECharts 图表逻辑 ====================
const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChartInstance = null
let pieChartInstance = null

const renderCharts = () => {
  renderTrendChart()
  renderPieChart()
}

// 🌟 提取主题配置颜色
const getChartColors = () => {
  const isDarkMode = isDark.value
  return {
    textColor: isDarkMode ? '#94a3b8' : '#64748b', // slate-400 : slate-500
    axisLineColor: isDarkMode ? '#334155' : '#cbd5e1', // slate-700 : slate-300
    splitLineColor: isDarkMode ? '#334155' : '#e2e8f0', // slate-700 : slate-200
    tooltipBg: isDarkMode ? 'rgba(15, 23, 42, 0.9)' : 'rgba(15, 23, 42, 0.9)', // 都是深色Tooltip
    pieBorderColor: isDarkMode ? '#1e293b' : '#fff', // slate-800 : white
    emptyPieColor: isDarkMode ? '#334155' : '#e2e8f0'
  }
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  if (!trendChartInstance) {
    trendChartInstance = echarts.init(trendChartRef.value)
  }

  const dateMap = {}
  dailyAuditList.value.forEach(o => {
    const d = o.date.substring(0, 10)
    if (!dateMap[d]) dateMap[d] = { rev: 0, profit: 0 }
    dateMap[d].rev += Number(o.revenue_usd)
    dateMap[d].profit += Number(o.profit_usd)
  })

  const sortedDates = Object.keys(dateMap).sort().slice(-15)
  const revData = sortedDates.map(d => dateMap[d].rev)
  const profitData = sortedDates.map(d => dateMap[d].profit)
  const colors = getChartColors()

  const option = {
    tooltip: {
      trigger: 'axis',
      confine: true, 
      appendToBody: true,
      axisPointer: { type: 'shadow' },
      backgroundColor: colors.tooltipBg,
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: function (params) {
        if (!params || params.length === 0) return tExt.value.emptyData
        let res = params[0].axisValue + '<br/>'
        params.forEach(item => {
          res += `${item.marker} ${item.seriesName}: $${Number(item.value).toFixed(2)}<br/>`
        })
        return res
      }
    },
    legend: {
      data: [tExt.value.chartRevenue, tExt.value.chartProfit],
      bottom: 0,
      icon: 'roundRect',
      textStyle: { color: colors.textColor, fontSize: 11, fontWeight: 'bold' }
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: sortedDates,
      axisLine: { lineStyle: { color: colors.axisLineColor } },
      axisLabel: { color: colors.textColor, fontSize: 10, fontFamily: 'monospace' }
    },
    yAxis: {
      type: 'value',
      name: tExt.value.chartAmount,
      nameTextStyle: { color: colors.textColor, fontSize: 10 },
      axisLabel: { color: colors.textColor, fontSize: 10, fontFamily: 'monospace' },
      splitLine: { lineStyle: { type: 'dashed', color: colors.splitLineColor } }
    },
    series: [
      {
        name: tExt.value.chartRevenue,
        type: 'bar',
        barWidth: '30%',
        itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] },
        data: revData,
        emphasis: { focus: 'series', itemStyle: { shadowBlur: 10, shadowColor: 'rgba(59,130,246,0.5)' } }
      },
      {
        name: tExt.value.chartProfit,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#10b981' },
        lineStyle: { width: 3, color: '#10b981' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.2)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
          ])
        },
        data: profitData,
        emphasis: { focus: 'series', scale: 1.5 }
      }
    ]
  }
  trendChartInstance.setOption(option)
}

const renderPieChart = () => {
  if (!pieChartRef.value) return
  if (!pieChartInstance) {
    pieChartInstance = echarts.init(pieChartRef.value)
  }

  const pb = paymentBreakdown.value
  const data = [
    { value: pb.cardPos.totalUSD, name: getPaymentMethodLabel('Card_POS') },
    { value: pb.pagoMovil.totalUSD, name: getPaymentMethodLabel('Pago_Movil') },
    { value: pb.cashBs.totalUSD, name: getPaymentMethodLabel('Cash_Bs') },
    { value: pb.cashUSD.totalUSD, name: getPaymentMethodLabel('Cash_USD') },
    { value: pb.pagoMixto.totalUSD, name: getPaymentMethodLabel('Pago_Mixto') }
  ].filter(item => item.value > 0)

  if (data.length === 0) {
    data.push({ value: 1, name: tExt.value.emptyData })
  }
  const colors = getChartColors()

  const option = {
    tooltip: {
      trigger: 'item',
      confine: true,
      appendToBody: true,
      backgroundColor: colors.tooltipBg,
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: function (params) {
        if (params.name === tExt.value.emptyData) return tExt.value.emptyData
        return `${params.marker} ${params.name}<br/>$${params.value.toFixed(2)} (${params.percent}%)`
      }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      icon: 'circle',
      textStyle: { color: colors.textColor, fontSize: 11, fontWeight: 'bold' }
    },
    color: data.length === 1 && data[0].name === tExt.value.emptyData ? [colors.emptyPieColor] : ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#6366f1'],
    series: [
      {
        name: tExt.value.paymentBreakdown,
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: colors.pieBorderColor,
          borderWidth: 2
        },
        label: { show: false },
        labelLine: { show: false },
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  pieChartInstance.setOption(option, true)
}

// 🌟 监听数据变化、语言变化和主题变化，重新渲染图表
watch([dailyAuditList, currentLang, isDark], () => {
  nextTick(() => {
    renderCharts()
  })
}, { deep: true })

const handleResize = () => {
  if (trendChartInstance) trendChartInstance.resize()
  if (pieChartInstance) pieChartInstance.resize()
}

let resizeObserver = null

onMounted(async () => {
  await fetchFinancialData()
  
  nextTick(() => {
    renderCharts()
    if (trendChartRef.value) {
      resizeObserver = new ResizeObserver(() => {
        handleResize()
      })
      resizeObserver.observe(trendChartRef.value)
    }
  })

  window.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleResize)
  if (resizeObserver) resizeObserver.disconnect()
  if (trendChartInstance) trendChartInstance.dispose()
  if (pieChartInstance) pieChartInstance.dispose()
})

const handleClickOutside = (e) => {
  const picker = document.querySelector('.absolute.top-full.right-0')
  if (isDatePickerVisible.value && picker && !picker.contains(e.target) && !e.target.closest('.relative')) {
    isDatePickerVisible.value = false
  }
}

// ... (exportProfitReport 保持不变，直接保留你原有的即可)
const exportProfitReport = () => {
  const ex = tExt.value
  const bcv = bcvRate.value

  let csvContent = "\uFEFF"
  csvContent += `${ex.exportTitle} (${startDate.value} ${ex.to} ${endDate.value})\n`
  csvContent += `${ex.rateLabel},${bcv}\n\n`

  csvContent += `${ex.coreMetrics}\n`
  csvContent += `${ex.revenue},$ ${analytics.value.total_revenue_usd.toFixed(2)},Bs. ${(analytics.value.total_revenue_usd * bcv).toFixed(2)}\n`
  csvContent += `${ex.cost},$ ${analytics.value.total_cost_usd.toFixed(2)},Bs. ${(analytics.value.total_cost_usd * bcv).toFixed(2)}\n`
  csvContent += `${ex.expenses},$ ${analytics.value.total_expenses_usd.toFixed(2)},Bs. ${(analytics.value.total_expenses_usd * bcv).toFixed(2)}\n`
  csvContent += `${ex.debt},$ ${analytics.value.total_debt_usd.toFixed(2)},Bs. ${(analytics.value.total_debt_usd * bcv).toFixed(2)}\n`
  csvContent += `${ex.netProfit},$ ${analytics.value.net_profit_usd.toFixed(2)},Bs. ${(analytics.value.net_profit_usd * bcv).toFixed(2)}\n\n`

  csvContent += `${ex.dailyDetails}\n`
  csvContent += `${ex.orderNo},${ex.time},${ex.payMethod},${ex.revenueUsd},${ex.revenueVes},${ex.costUsd},${ex.profitUsd},${ex.profitBs}\n`
  
  dailyAuditList.value.forEach(row => {
    const safeMethod = `"${getPaymentMethodLabel(row.payment_method)}"` 
    csvContent += `${row.id},${row.date},${safeMethod},${Number(row.revenue_usd).toFixed(2)},${(Number(row.revenue_usd) * bcv).toFixed(2)},${Number(row.cost_usd).toFixed(2)},${Number(row.profit_usd).toFixed(2)},${(Number(row.profit_usd) * bcv).toFixed(2)}\n`
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = `Profit_${startDate.value}_to_${endDate.value}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>