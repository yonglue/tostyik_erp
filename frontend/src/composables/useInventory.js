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
    const res = await apiFetch(url)
    if (!res.ok) return null
    return await res.json()
  } catch (e) {
    return null
  }
}

// 🌟 辅助函数：从 localStorage 检查当前用户是否具备指定权限
const checkUserPermission = (permKey) => {
  try {
    const stored = localStorage.getItem('tostiyk_current_user')
    if (!stored) return false
    const user = JSON.parse(stored)
    const role = user.role || 'staff'
    const perms = user.permissions || []
    if (role === 'super_admin' || role === 'admin' || perms.includes('*')) return true
    return perms.includes(permKey)
  } catch (e) {
    return false
  }
}

export function useInventory() {
  const fetchParts = async () => {
    if (!checkUserPermission('parts:view')) return
    const data = await safeJson('/api/parts')
    if (data) partsList.value = data
  }
  const fetchClients = async () => {
    if (!checkUserPermission('clients:view')) return
    const data = await safeJson('/api/clients')
    if (data) clientsList.value = data
  }
  const fetchTransactions = async () => {
    if (!checkUserPermission('transactions:history')) return
    const data = await safeJson('/api/transactions')
    if (data) transactionsList.value = data
  }
  const fetchQuotations = async () => {
    if (!checkUserPermission('pos:access')) return  // 🛡️ 没有 POS / 开单权限时，禁止静默拉取报价单，避免 401 报错
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

  /** 一次刷新全部列表（开单/删改后调用），内部自动做权限过滤 */
  const refreshAll = () => {
    const tasks = [fetchDashboardStats(), fetchBcvRate()]
    if (checkUserPermission('parts:view')) tasks.push(fetchParts())
    if (checkUserPermission('clients:view')) tasks.push(fetchClients())
    if (checkUserPermission('transactions:history')) tasks.push(fetchTransactions())
    if (checkUserPermission('pos:access')) tasks.push(fetchQuotations())
    return Promise.all(tasks)
  }

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