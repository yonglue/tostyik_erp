<!-- src/components/InventoryAuditView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">
    
    <!-- ==================== 第一层：页面大标题与 Tab 切换 ==================== -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span>📋</span> 库存盘点（实体清点）
        </h2>
        <p class="text-xs text-slate-500 mt-1">请录入实际清点的数量。留空的商品将被系统忽略，不参与本次盘点。</p>
      </div>

      <!-- Tab 切换 -->
      <div class="flex bg-slate-200/60 p-1 rounded-xl shrink-0">
        <button 
          @click="activeTab = 'audit'"
          :class="activeTab === 'audit' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
        >
          盘点操作
        </button>
        <button 
          @click="activeTab = 'history'; fetchHistory()"
          :class="activeTab === 'history' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
        >
          历史盘点记录
        </button>
      </div>
    </div>

    <!-- ==================== 第二层：操作工具栏（根据 Tab 切换） ==================== -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      
      <!-- 盘点操作 Tab 的工具栏 -->
      <template v-if="activeTab === 'audit'">
        <!-- 左侧：实时盈亏统计 -->
        <div class="flex items-center gap-4 bg-slate-50 px-4 py-2 rounded-xl border border-slate-200">
          <div class="text-center">
            <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">盘盈 (资产增加)</div>
            <div class="text-sm font-black text-emerald-600 font-mono">+ ${{ totalProfitAmount.toFixed(2) }}</div>
          </div>
          <div class="w-px h-6 bg-slate-300"></div>
          <div class="text-center">
            <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">盘亏 (资产损失)</div>
            <div class="text-sm font-black text-rose-600 font-mono">- ${{ totalLossAmount.toFixed(2) }}</div>
          </div>
        </div>

        <!-- 右侧：搜索与操作按钮 -->
        <div class="flex items-center gap-3 flex-wrap">
          <div class="relative w-full sm:w-64">
            <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="搜索 OEM 或 配件名称..." 
              class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500"
            />
          </div>
          
          <button 
            @click="exportAuditDiff" 
            :disabled="hasNoChanges"
            class="bg-emerald-50 hover:bg-emerald-100 disabled:bg-slate-100 disabled:text-slate-400 text-emerald-700 border border-emerald-200 px-5 py-2.5 rounded-xl font-bold transition-all cursor-pointer flex items-center gap-2"
          >
            <span>📥</span> 导出差异表
          </button>

          <button 
            @click="submitAudit" 
            :disabled="hasNoChanges || isSubmitting"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white px-6 py-2.5 rounded-xl font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer flex items-center gap-2"
          >
            <span>💾</span> {{ isSubmitting ? '提交中...' : '提交盘点结果' }}
          </button>
        </div>
      </template>

      <!-- 历史记录 Tab 的工具栏 -->
      <template v-if="activeTab === 'history'">
        <div>
          <h3 class="font-bold text-slate-800">历史盘点单据</h3>
          <p class="text-xs text-slate-500 mt-1">系统自动汇总的盘点盈亏流水（来源：进销存系统）</p>
        </div>
        <button @click="fetchHistory" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-xl text-xs font-bold text-slate-600 transition-colors cursor-pointer flex items-center gap-1.5">
          🔄 刷新记录
        </button>
      </template>

    </div>

    <!-- ==================== 第三层：数据主体区 ==================== -->
    
    <!-- 盘点明细表 -->
    <div v-if="activeTab === 'audit'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-4 px-6">商品信息</th>
              <th class="py-4 px-6 text-center">系统库存</th>
              <th class="py-4 px-6 text-center">实盘数量</th>
              <th class="py-4 px-6 text-center">盈亏差异</th>
              <th class="py-4 px-6">差异原因 (选填)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="item in filteredParts" :key="item.id" class="hover:bg-blue-50/30 transition-colors">
              <td class="py-4 px-6">
                <div class="font-bold text-slate-800">{{ item.name }}</div>
                <div class="text-xs font-mono text-blue-600 mt-1">{{ item.oem }} <span class="text-slate-400 ml-1">| {{ item.brand }}</span></div>
                <div class="text-[10px] text-slate-400 mt-0.5">进价: ${{ (item.cost_price || 0).toFixed(2) }}</div>
              </td>
              <td class="py-4 px-6 text-center font-mono font-bold text-slate-500">
                {{ item.stock }}
              </td>
              <td class="py-4 px-6 text-center">
                <input 
                  v-model.number="auditForm[item.id]" 
                  type="number" 
                  min="0"
                  placeholder="未盘"
                  class="w-24 text-center bg-white border border-slate-300 rounded-lg px-3 py-2 font-mono font-black text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 placeholder:text-slate-300 placeholder:font-normal"
                />
              </td>
              <td class="py-4 px-6 text-center font-mono font-black">
                <span v-if="auditForm[item.id] === null || auditForm[item.id] === ''" class="text-slate-300">-</span>
                <span v-else-if="getDiff(item) === 0" class="text-slate-400">0</span>
                <span v-else-if="getDiff(item) > 0" class="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">+{{ getDiff(item) }}</span>
                <span v-else class="text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-100">{{ getDiff(item) }}</span>
              </td>
              <td class="py-4 px-6">
                <input 
                  v-model="reasons[item.id]" 
                  type="text" 
                  placeholder="例如：破损、丢失..."
                  class="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500 disabled:opacity-50"
                  :disabled="auditForm[item.id] === null || auditForm[item.id] === '' || getDiff(item) === 0"
                />
              </td>
            </tr>
            <tr v-if="filteredParts.length === 0">
              <td colspan="5" class="py-16 text-center text-slate-400 text-sm font-bold">
                📭 没有找到符合条件的商品
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 历史盘点表 -->
    <div v-if="activeTab === 'history'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-4 px-6">盘点时间 / 批次 / 经办人</th>
              <th class="py-4 px-6">商品信息</th>
              <th class="py-4 px-6 text-center">变动类型</th>
              <th class="py-4 px-6 text-center">变动数量</th>
              <th class="py-4 px-6 text-right">按进价折算金额</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="isFetchingHistory" class="text-center">
              <td colspan="5" class="py-10 text-slate-400 text-xs">加载中...</td>
            </tr>
            <tr v-else-if="historyList.length === 0" class="text-center">
              <td colspan="5" class="py-16 text-slate-400 text-xs font-bold">📭 暂无历史盘点记录</td>
            </tr>
            <tr v-for="tx in historyList" :key="tx.id" class="hover:bg-blue-50/30 transition-colors">
              <td class="py-4 px-6">
                <div class="font-mono text-xs text-slate-600">{{ tx.timestamp }}</div>
                <div class="text-[10px] text-blue-600 font-bold mt-1">批次: {{ parseTxInfo(tx.customer_or_supplier).batch }}</div>
                <div class="text-[10px] text-slate-500 mt-0.5">经办: {{ parseTxInfo(tx.customer_or_supplier).operator }}</div>
              </td>
              <td class="py-4 px-6">
                <div class="font-bold text-slate-800">{{ tx.part_name }}</div>
                <div class="text-xs font-mono text-slate-400 mt-0.5">{{ tx.part_oem }}</div>
              </td>
              <td class="py-4 px-6 text-center">
                <span v-if="tx.type === 'IN'" class="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-md text-xs font-bold">
                  盘盈 (IN)
                </span>
                <span v-else class="bg-rose-50 text-rose-700 border border-rose-200 px-2.5 py-1 rounded-md text-xs font-bold">
                  盘亏 (OUT)
                </span>
              </td>
              <td class="py-4 px-6 text-center font-mono font-black" :class="tx.type === 'IN' ? 'text-emerald-600' : 'text-rose-600'">
                {{ tx.type === 'IN' ? '+' : '-' }}{{ tx.quantity }}
              </td>
              <td class="py-4 px-6 text-right font-mono font-bold text-slate-700">
                $ {{ Number(tx.total_amount || 0).toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { Search } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'

const { showSuccessModal } = useNotifications()

const activeTab = ref('audit')
const parts = ref([])
const searchQuery = ref('')
const isSubmitting = ref(false)

const auditForm = reactive({})
const reasons = reactive({})

const fetchParts = async () => {
  try {
    const res = await apiFetch('/api/parts')
    if (res.ok) {
      parts.value = await res.json()
      parts.value.forEach(p => {
        auditForm[p.id] = null
        reasons[p.id] = ''
      })
    }
  } catch (e) { console.error(e) }
}

const filteredParts = computed(() => {
  if (!searchQuery.value) return parts.value
  const q = searchQuery.value.toLowerCase()
  return parts.value.filter(p => 
    p.oem.toLowerCase().includes(q) || 
    p.name.toLowerCase().includes(q)
  )
})

const getDiff = (item) => {
  const rawVal = auditForm[item.id]
  if (rawVal === null || rawVal === undefined || rawVal === '') return 0
  const actual = Number(rawVal)
  return isNaN(actual) ? 0 : actual - item.stock
}

const totalProfitAmount = computed(() => {
  return parts.value.reduce((sum, p) => {
    const diff = getDiff(p)
    return diff > 0 ? sum + (diff * (p.cost_price || 0)) : sum
  }, 0)
})

const totalLossAmount = computed(() => {
  return parts.value.reduce((sum, p) => {
    const diff = getDiff(p)
    return diff < 0 ? sum + (Math.abs(diff) * (p.cost_price || 0)) : sum
  }, 0)
})

const hasNoChanges = computed(() => {
  return parts.value.every(p => {
    const rawVal = auditForm[p.id]
    if (rawVal === null || rawVal === undefined || rawVal === '') return true
    return getDiff(p) === 0
  })
})

const submitAudit = async () => {
  if (hasNoChanges.value) return
  
  const diffItems = parts.value
    .filter(p => {
      const rawVal = auditForm[p.id]
      if (rawVal === null || rawVal === undefined || rawVal === '') return false
      return getDiff(p) !== 0
    })
    .map(p => ({
      part_id: p.id,
      actual_stock: Number(auditForm[p.id]),
      reason: reasons[p.id] || ''
    }))

  if (diffItems.length === 0) {
    showSuccessModal('⚠️ 没有需要提交的盘点差异')
    return
  }

  isSubmitting.value = true
  try {
    const res = await apiFetch('/api/inventory/audit', {
      method: 'POST',
      body: JSON.stringify({ items: diffItems })
    })
    
    if (res.ok) {
      const data = await res.json()
      showSuccessModal(`✅ ${data.message}`)
      fetchParts()
      if (activeTab.value === 'history') fetchHistory()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 盘点提交失败: ${err.detail}`)
    }
  } catch (e) {
    showSuccessModal('❌ 网络异常')
  } finally {
    isSubmitting.value = false
  }
}

// ==================== 🌟 导出盘点差异 CSV ====================
const exportAuditDiff = () => {
  const diffItems = parts.value.filter(p => {
    const rawVal = auditForm[p.id]
    if (rawVal === null || rawVal === undefined || rawVal === '') return false
    return getDiff(p) !== 0
  })

  if (diffItems.length === 0) {
    showSuccessModal('⚠️ 当前没有盘点差异可以导出')
    return
  }

  let csvContent = "\uFEFF" 
  csvContent += "OEM 编号,配件名称,适配品牌,系统库存,实盘数量,盈亏差异,进价 (USD),差异金额 (USD),差异原因\r\n"

  diffItems.forEach(item => {
    const diff = getDiff(item)
    const cost = Number(item.cost_price) || 0
    const amount = Math.abs(diff) * cost
    const reason = reasons[item.id] || '未填写'

    const row = [
      `"${item.oem}"`,
      `"${item.name}"`,
      `"${item.brand || ''}"`,
      item.stock,
      auditForm[item.id],
      diff > 0 ? `+${diff}` : diff,
      cost.toFixed(2),
      amount.toFixed(2),
      `"${reason}"`
    ].join(",")
    
    csvContent += row + "\r\n"
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10)
  const timeStr = now.toTimeString().slice(0, 5).replace(':', '')
  link.download = `盘点差异_${dateStr}_${timeStr}.csv`
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// ==================== 🌟 历史盘点数据 ====================
const historyList = ref([])
const isFetchingHistory = ref(false)

const fetchHistory = async () => {
  isFetchingHistory.value = true
  try {
    const res = await apiFetch('/api/transactions')
    if (res.ok) {
      const allTxs = await res.json()
      historyList.value = allTxs.filter(tx => tx.customer_or_supplier?.includes('库存盘点调整'))
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 获取盘点历史失败')
  } finally {
    isFetchingHistory.value = false
  }
}

const parseTxInfo = (infoStr) => {
  if (!infoStr) return { batch: '-', operator: '-' }
  const parts = infoStr.split('|')
  if (parts.length >= 3) {
    return { batch: parts[1], operator: parts[2] }
  }
  return { batch: '历史记录', operator: '-' }
}

onMounted(() => {
  fetchParts()
  fetchHistory() 
})
</script>