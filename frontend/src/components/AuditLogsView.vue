<!-- src/components/AuditLogsView.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'

const { t } = useI18n()
const logsList = ref([])
const loading = ref(false)

// 🌟 筛选条件状态
const filterUsername = ref('')
const filterRole = ref('')
const filterAction = ref('')
const filterDate = ref('')

// 🌟 现代提示弹窗状态
const warningModalVisible = ref(false)
const warningMessage = ref('')

const showWarning = (msg) => {
  warningMessage.value = msg
  warningModalVisible.value = true
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await apiFetch('/api/audit-logs')
    if (res.ok) {
      logsList.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// 🌟 一键导出当前筛选后的审计日志 (CSV)
const exportAuditLogsCsv = () => {
  if (filteredLogs.value.length === 0) {
    showWarning(t.value.exportEmptyError)
    return
  }

  let csvContent = "\uFEFF"
  csvContent += "ID,Username,Role,Action,Details,Timestamp\r\n"

  filteredLogs.value.forEach(log => {
    const detailsClean = `"${(log.details || '').replace(/"/g, '""')}"`
    const row = [
      log.id,
      log.username,
      log.role,
      log.action,
      detailsClean,
      log.created_at
    ].join(",")
    csvContent += row + "\r\n"
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.setAttribute("href", url)
  
  const dateStr = new Date().toISOString().slice(0, 10)
  link.setAttribute("download", `tostiyk_audit_logs_${dateStr}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 🌟 前端高能过滤计算属性
const filteredLogs = computed(() => {
  return logsList.value.filter(log => {
    const matchUser = !filterUsername.value || log.username.toLowerCase().includes(filterUsername.value.toLowerCase())
    const matchRole = !filterRole.value || log.role === filterRole.value
    const matchAction = !filterAction.value || log.action === filterAction.value
    const matchDate = !filterDate.value || (log.created_at && log.created_at.startsWith(filterDate.value))

    return matchUser && matchRole && matchAction && matchDate
  })
})

const resetFilters = () => {
  filterUsername.value = ''
  filterRole.value = ''
  filterAction.value = ''
  filterDate.value = ''
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div class="space-y-6 max-w-6xl mx-auto">
    <!-- 头部标题与一键导出按钮 -->
    <div class="bg-white p-6 rounded-2xl shadow-xs border border-slate-100 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="font-bold text-lg text-slate-800">🛡️ {{ t.auditTitle }}</h2>
        <p class="text-xs text-slate-400 mt-0.5">{{ t.auditSub }}</p>
      </div>
      <div class="flex items-center gap-2.5">
        <button @click="exportAuditLogsCsv" class="px-4 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 border border-emerald-200/60 shadow-xs cursor-pointer">
          <span>📥</span> {{ t.exportLogsBtn }}
        </button>
        <button @click="fetchLogs" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer">
          <span>🔄</span> {{ t.auditRefresh }}
        </button>
      </div>
    </div>

    <!-- 🌟 高级筛选控制面板 -->
    <div class="bg-white p-5 rounded-2xl shadow-xs border border-slate-100 grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">🔍 {{ t.auditFilterUser }}</label>
        <input v-model="filterUsername" type="text" :placeholder="t.auditUserPlaceholder" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">🛡️ {{ t.auditFilterRole }}</label>
        <select v-model="filterRole" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500 cursor-pointer">
          <option value="">{{ t.auditAllRoles }}</option>
          <option value="super_admin">SUPER_ADMIN</option>
          <option value="admin">ADMIN</option>
          <option value="staff">STAFF</option>
          <option value="cashier">CASHIER</option>
          <option value="warehouse">WAREHOUSE</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-500 mb-1">⚡ {{ t.auditFilterAction }}</label>
        <select v-model="filterAction" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500 cursor-pointer">
          <option value="">{{ t.auditAllActions }} (全部操作)</option>
          <option value="CREATE_QUOTATION">🛒 开单挂账成交 (Create Quotation)</option>
          <option value="CLIENT_REPAYMENT">💰 客户还款销账 (Client Repayment)</option>
          <option value="UPDATE_STOCK">📦 库存进出变动 (Update Stock)</option>
          <option value="CREATE_PART">➕ 新增配件商品 (Create Part)</option>
          <option value="DELETE_PART">🗑️ 删除配件商品 (Delete Part)</option>
          <option value="CREATE_CLIENT">👥 新增客户档案 (Create Client)</option>
          <option value="DELETE_CLIENT">❌ 删除客户档案 (Delete Client)</option>
          <option value="CREATE_STAFF">👨‍💼 新增员工账号 (Create Staff)</option>
          <option value="DELETE_STAFF">🚫 删除员工账号 (Delete Staff)</option>
          <option value="EXPORT_AUDIT_LOGS">📥 导出审计报表 (Export Logs)</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <label class="block text-xs font-semibold text-slate-500 mb-1">📅 {{ t.auditFilterDate }}</label>
          <input v-model="filterDate" type="date" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500 font-mono" />
        </div>
        <button @click="resetFilters" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-semibold transition-colors mt-5 cursor-pointer" :title="t.auditReset">
          {{ t.auditReset }}
        </button>
      </div>
    </div>

    <!-- 日志表格 -->
    <div class="bg-white rounded-2xl shadow-xs border border-slate-100 overflow-hidden">
      <div class="px-6 py-3 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>{{ t.auditDisplayCount }}: <strong class="text-slate-800">{{ filteredLogs.length }}</strong> / {{ t.auditTotalCount }} {{ logsList.length }} {{ t.auditCountSuffix }}</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase">
              <th class="px-6 py-3">{{ t.colLogId }}</th>
              <th class="px-6 py-3">{{ t.colUser }}</th>
              <th class="px-6 py-3">{{ t.colRole }}</th>
              <th class="px-6 py-3">{{ t.colAction }}</th>
              <th class="px-6 py-3">{{ t.colDetails }}</th>
              <th class="px-6 py-3 text-right">{{ t.colTimestamp }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-xs">
            <tr v-for="log in filteredLogs" :key="log.id" class="hover:bg-slate-50/50">
              <td class="px-6 py-4 font-mono text-slate-400">#{{ log.id }}</td>
              <td class="px-6 py-4 font-bold text-slate-800 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                {{ log.username }}
              </td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 rounded-lg font-semibold text-[10px]" :class="log.role === 'super_admin' ? 'bg-purple-50 text-purple-600' : 'bg-blue-50 text-blue-600'">
                  {{ (log.role || '').toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4 font-mono font-semibold text-slate-700">
                <span class="px-2 py-1 rounded-md text-[11px]" :class="log.action === 'CREATE_QUOTATION' ? 'bg-emerald-100 text-emerald-800 font-bold' : 'bg-slate-100 text-slate-700'">
                  {{ log.action }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-600 max-w-xs truncate" :title="log.details">
                {{ log.details }}
              </td>
              <td class="px-6 py-4 text-right font-mono text-slate-400">
                {{ log.created_at }}
              </td>
            </tr>
            <tr v-if="filteredLogs.length === 0 && !loading">
              <td colspan="6" class="px-6 py-12 text-center text-slate-400">{{ t.auditEmpty }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 🌟 精美现代提示弹窗 -->
    <div v-if="warningModalVisible" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-sm w-full overflow-hidden border border-slate-100 p-6 space-y-5 text-center animate-in fade-in zoom-in-95 duration-150">
        <div class="w-12 h-12 rounded-2xl bg-amber-500 mx-auto flex items-center justify-center text-white shadow-lg shadow-amber-500/30 text-xl font-bold">
          ⚠️
        </div>
        <div class="space-y-1">
          <h3 class="font-bold text-base text-slate-900">{{ t.warningTitle }}</h3>
          <p class="text-xs text-slate-500 leading-relaxed">{{ warningMessage }}</p>
        </div>
        <button @click="warningModalVisible = false" class="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-md transition-colors cursor-pointer">
          {{ t.btnOk }}
        </button>
      </div>
    </div>
  </div>
</template>