<!-- src/components/CashRegisterView.vue -->
<template>
  <div class="space-y-6">
    <!-- 顶部标题与日期选择器 -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-bold text-slate-900">📊 {{ t.salesOverview || '销售概览与收银交接对账' }} (Sales & Shift Analytics)</h2>
        <p class="text-xs text-slate-500 mt-0.5">{{ t.salesOverviewSubtitle || '实时监控每日营业额、多币种支付拆分及历史交接班盲盘审计' }}</p>
      </div>
      <div class="flex items-center gap-3">
        <label class="text-xs font-semibold text-slate-600">{{ t.selectDate || '选择日期' }}:</label>
        <input 
          v-model="selectedDate" 
          type="date" 
          :lang="currentLang === 'es' ? 'es' : (currentLang === 'en' ? 'en' : 'zh')"
          placeholder="YYYY-MM-DD"
          @change="fetchSalesOverview"
          class="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono outline-none focus:border-blue-500 w-32 text-center"
        />
        <button 
          @click="selectedDate = ''; fetchSalesOverview()" 
          class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-semibold transition-colors cursor-pointer"
        >
          {{ t.viewAllOrToday || '全部/今日' }}
        </button>
      </div>
    </div>

    <!-- 核心指标大卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <!-- 今日/选中日期营业额 -->
      <div class="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-6 rounded-2xl shadow-lg shadow-blue-500/20">
        <p class="text-xs font-medium text-blue-100 uppercase tracking-wider">{{ t.selectedDateRevenue || '选中日期营业额' }}</p>
        <h3 class="text-3xl font-extrabold mt-2">$ {{ overviewData.daily_total_usd.toFixed(2) }}</h3>
        <p class="text-xs text-blue-200 mt-1 font-mono">≈ Bs. {{ overviewData.daily_total_bs.toFixed(2) }} (BCV)</p>
      </div>

      <!-- 历史总营业额 -->
      <div class="bg-gradient-to-br from-emerald-600 to-emerald-700 text-white p-6 rounded-2xl shadow-lg shadow-emerald-500/20">
        <p class="text-xs font-medium text-emerald-100 uppercase tracking-wider">{{ t.historyTotalRevenue || '历史总营业额' }}</p>
        <h3 class="text-3xl font-extrabold mt-2">$ {{ overviewData.history_total_usd.toFixed(2) }}</h3>
        <p class="text-xs text-emerald-200 mt-1">{{ t.totalOrders || '总订单数' }}: <span class="font-bold">{{ overviewData.history_total_transactions }}</span> {{ t.ordersUnit || '单' }}</p>
      </div>

      <!-- 历史总销量 SKU 件数 -->
      <div class="bg-gradient-to-br from-slate-800 to-slate-900 text-white p-6 rounded-2xl shadow-lg">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">{{ t.historyTotalItems || '历史配件总销量' }}</p>
        <h3 class="text-3xl font-extrabold mt-2 font-mono">{{ overviewData.history_total_skus_sold }} <span class="text-sm font-normal text-slate-400">{{ t.pieces || '件' }}</span></h3>
        <p class="text-xs text-slate-400 mt-1">{{ t.inventoryHealthy || '库存状态健康' }}</p>
      </div>
    </div>

    <!-- 收款方式明细拆分 -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
      <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider">💵 {{ t.paymentBreakdown || '多币种收款渠道拆分' }}</h3>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
          <p class="text-xs font-semibold text-slate-500">💵 Cash USD</p>
          <p class="text-lg font-extrabold text-slate-900 mt-1">$ {{ (overviewData.payment_breakdown?.Cash_USD || 0).toFixed(2) }}</p>
        </div>
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
          <p class="text-xs font-semibold text-slate-500">📱 Zelle</p>
          <p class="text-lg font-extrabold text-blue-600 mt-1">$ {{ (overviewData.payment_breakdown?.Zelle || 0).toFixed(2) }}</p>
        </div>
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
          <p class="text-xs font-semibold text-slate-500">⚡ Pago Móvil</p>
          <p class="text-lg font-extrabold text-amber-600 mt-1">$ {{ (overviewData.payment_breakdown?.Pago_Movil || 0).toFixed(2) }}</p>
        </div>
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
          <p class="text-xs font-semibold text-slate-500">🏦 Transfer Bs.</p>
          <p class="text-lg font-extrabold text-purple-600 mt-1">$ {{ (overviewData.payment_breakdown?.Transfer_Bs || 0).toFixed(2) }}</p>
        </div>
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
          <p class="text-xs font-semibold text-slate-500">🪙 USDT</p>
          <p class="text-lg font-extrabold text-emerald-600 mt-1">$ {{ (overviewData.payment_breakdown?.USDT || 0).toFixed(2) }}</p>
        </div>
      </div>
    </div>

    <!-- 🌟 历史交接班与盲盘点钞审计表格 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <h3 class="font-bold text-sm text-slate-800 flex items-center gap-2">
          <span>📊 历史交接班与盲盘点钞审计记录 (Shift Handover Audit Logs)</span>
        </h3>
        <span class="text-xs font-mono text-slate-500">共 {{ shiftRecords.length }} 班交班记录</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-4">交班时间</th>
              <th class="py-3 px-4">收银员</th>
              <th class="py-3 px-4 text-right">系统现金应收</th>
              <th class="py-3 px-4 text-right">实盘现金(USD)</th>
              <th class="py-3 px-4 text-right">Zelle / PagoMóvil</th>
              <th class="py-3 px-4 text-right">现金盈亏差额</th>
              <th class="py-3 px-4">盈亏备注</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-xs font-mono">
            <tr v-for="record in shiftRecords" :key="record.id" class="hover:bg-slate-50/50">
              <td class="py-3.5 px-4 text-slate-600">{{ record.closed_at }}</td>
              <td class="py-3.5 px-4 font-bold text-slate-900">{{ record.operator }}</td>
              <td class="py-3.5 px-4 text-right text-slate-700">$ {{ record.system_cash_usd.toFixed(2) }}</td>
              <td class="py-3.5 px-4 text-right font-extrabold text-blue-600">$ {{ record.actual_cash_usd.toFixed(2) }}</td>
              <td class="py-3.5 px-4 text-right text-slate-600">
                Z: $ {{ Number(record.system_zelle ? record.system_zelle : 0).toFixed(2) }} &nbsp; P: $ {{ Number(record.system_pago_movil ? record.system_pago_movil : 0).toFixed(2) }}
              </td>
              <td class="py-3.5 px-4 text-right font-bold">
                <span :class="(record.actual_cash_usd - record.system_cash_usd) === 0 ? 'text-emerald-600' : ((record.actual_cash_usd - record.system_cash_usd) > 0 ? 'text-blue-600' : 'text-rose-600')">
                  {{ (record.actual_cash_usd - record.system_cash_usd) >= 0 ? '+' : '' }}$ {{ (record.actual_cash_usd - record.system_cash_usd).toFixed(2) }}
                </span>
              </td>
              <td class="py-3.5 px-4 text-slate-500 italic">{{ record.notes || '无备注 (平账)' }}</td>
            </tr>
            <tr v-if="shiftRecords.length === 0">
              <td colspan="7" class="py-8 text-center text-slate-400 text-xs">暂无历史交班归档记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 当日/选中日期商品销售明细表格 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-5 border-b border-slate-100 flex items-center justify-between">
        <h3 class="font-bold text-sm text-slate-800">📦 {{ t.productSalesBreakdown || '商品销售明细排行' }}</h3>
        <span class="text-xs font-mono text-slate-500">{{ t.totalTypes || '共' }} {{ overviewData.product_sales_items?.length || 0 }} {{ t.partsUnit || '种配件' }}</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-6">{{ t.colOem || 'OEM 编号' }}</th>
              <th class="py-3 px-6">{{ t.colName || '配件名称' }}</th>
              <th class="py-3 px-6 text-center">{{ t.salesQty || '销售数量' }}</th>
              <th class="py-3 px-6 text-right">{{ t.salesTotalUsd || '销售总额 (USD)' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="item in overviewData.product_sales_items" :key="item.oem" class="hover:bg-slate-50/50">
              <td class="py-3.5 px-6 font-mono font-bold text-slate-800">{{ item.oem }}</td>
              <td class="py-3.5 px-6 font-medium text-slate-900">{{ item.name }}</td>
              <td class="py-3.5 px-6 text-center font-bold text-blue-600">{{ item.total_qty }}</td>
              <td class="py-3.5 px-6 text-right font-extrabold text-emerald-600">$ {{ item.total_amount.toFixed(2) }}</td>
            </tr>
            <tr v-if="!overviewData.product_sales_items || overviewData.product_sales_items.length === 0">
              <td colspan="4" class="py-8 text-center text-slate-400 text-xs">{{ t.noSalesData || '当前时间段暂无销售记录' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 详细出库流水日志 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-5 border-b border-slate-100">
        <h3 class="font-bold text-sm text-slate-800">⏱️ {{ t.transactionLog || '详细出库流水日志' }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-6">{{ t.txTime || '时间' }}</th>
              <th class="py-3 px-6">{{ t.colOem || 'OEM 编号' }}</th>
              <th class="py-3 px-6">{{ t.colName || '配件名称' }}</th>
              <th class="py-3 px-6 text-center">{{ t.colStock || '数量' }}</th>
              <th class="py-3 px-6">{{ t.unitPrice || '单价 (USD)' }}</th>
              <th class="py-3 px-6">{{ t.subtotal || '小计 (USD)' }}</th>
              <th class="py-3 px-6">{{ t.client || '客户 / 摘要' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-xs">
            <tr v-for="tx in overviewData.raw_transactions" :key="tx.id" class="hover:bg-slate-50/50">
              <td class="py-3 px-6 font-mono text-slate-500">{{ tx.timestamp }}</td>
              <td class="py-3 px-6 font-mono font-bold text-slate-800">{{ tx.oem }}</td>
              <td class="py-3 px-6 font-medium text-slate-900">{{ tx.name }}</td>
              <td class="py-3 px-6 text-center font-bold text-blue-600">{{ tx.quantity }}</td>
              <td class="py-3 px-6">$ {{ tx.unit_price.toFixed(2) }}</td>
              <td class="py-3 px-6 font-bold text-emerald-600">$ {{ tx.total_amount.toFixed(2) }}</td>
              <td class="py-3 px-6 text-slate-600 font-semibold">{{ tx.customer }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiUrl, apiFetch } from '../utils/api'

const { t, currentLang } = useI18n()
const selectedDate = ref('')
const overviewData = ref({
  daily_total_usd: 0,
  daily_total_bs: 0,
  payment_breakdown: {},
  product_sales_items: [],
  history_total_usd: 0,
  history_total_transactions: 0,
  history_total_skus_sold: 0,
  raw_transactions: []
})

// 历史交接班记录状态
const shiftRecords = ref([])

const fetchSalesOverview = async () => {
  try {
    let url = apiUrl('/api/sales/overview')
    if (selectedDate.value) {
      url += `?target_date=${selectedDate.value}`
    }
    const res = await fetch(url)
    if (res.ok) {
      overviewData.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

// 获取历史交接班记录
const fetchShiftRecords = async () => {
  try {
    const res = await apiFetch('/api/pos/shift-records')
    if (res.ok) {
      shiftRecords.value = await res.json()
    }
  } catch (e) {
    console.error('获取历史交班记录失败:', e)
  }
}

onMounted(() => {
  fetchSalesOverview()
  fetchShiftRecords()
})
</script>