// src/composables/useInventory.js
//
// 库存/客户/流水/报价/看板数据与取数函数。

import { computed, ref } from 'vue'
import { apiFetch } from '../utils/api'

const bcvRate = ref(36.50)
const partsList = ref([])
const clientsList = ref([])
const transactionsList = ref([])
const quotationsList = ref([])

const stats = ref({
  total_inventory_usd: 0, total_inventory_bs: 0,
  total_sales_usd: 0, total_sales_bs: 0,
  total_skus: 0, low_stock_count: 0
})

/** 安全取 JSON：失败时保持原值，避免一个接口挂掉导致整个页面空白 */
async function safeJson(url) {
  try {
    return await (await apiFetch(url)).json()
  } catch (e) {
    return null
  }
}

export function useInventory() {
  const fetchParts = async () => {
    const data = await safeJson('/api/parts')
    if (data) partsList.value = data
  }
  const fetchClients = async () => {
    const data = await safeJson('/api/clients')
    if (data) clientsList.value = data
  }
  const fetchTransactions = async () => {
    const data = await safeJson('/api/transactions')
    if (data) transactionsList.value = data
  }
  const fetchQuotations = async () => {
    const data = await safeJson('/api/quotations')
    if (data) quotationsList.value = data
  }
  const fetchDashboardStats = async () => {
    const data = await safeJson('/api/dashboard/stats')
    if (data) stats.value = data
  }
  const fetchBcvRate = async () => {
    const data = await safeJson('/api/bcv-rate')
    if (data) bcvRate.value = data.rate
  }

  /** 一次刷新全部列表（开单/删改后调用） */
  const refreshAll = () => Promise.all([
    fetchParts(), fetchClients(), fetchTransactions(),
    fetchQuotations(), fetchDashboardStats()
  ])

  const brandsList = computed(() => [
    'ALL',
    ...Array.from(new Set(partsList.value.map((p) => p.brand)))
  ])

  return {
    bcvRate,
    partsList,
    clientsList,
    transactionsList,
    quotationsList,
    stats,
    brandsList,
    fetchParts,
    fetchClients,
    fetchTransactions,
    fetchQuotations,
    fetchDashboardStats,
    fetchBcvRate,
    refreshAll
  }
}
