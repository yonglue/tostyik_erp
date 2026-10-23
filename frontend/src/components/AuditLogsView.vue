<!-- src/components/AuditLogsView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">
    <!-- 头部标题与一键导出按钮 -->
    <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-xs border border-slate-200/80 dark:border-slate-700 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="font-bold text-lg text-slate-800 dark:text-slate-200 flex items-center gap-2">
          <span>🛡️</span> {{ tExt.title }}
        </h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ tExt.subtitle }}</p>
      </div>
      <div class="flex items-center gap-2.5">
        <button @click="exportAuditLogsCsv" class="px-4 py-2 bg-emerald-50 dark:bg-emerald-900/30 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-400 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 border border-emerald-200/60 dark:border-emerald-800 shadow-xs cursor-pointer">
          <span>📥</span> {{ tExt.exportBtn }}
        </button>
        <button @click="fetchLogs" class="px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer">
          <span>🔄</span> {{ t.common.refresh }}
        </button>
      </div>
    </div>

    <!-- 高级筛选控制面板 -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-xs border border-slate-200/80 dark:border-slate-700 grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
      <div>
        <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">🔍 {{ tExt.filterUser }}</label>
        <input v-model="filterUsername" type="text" :placeholder="tExt.phUser" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500 focus:bg-white dark:focus:bg-slate-900 dark:text-white transition-all" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">🛡️ {{ tExt.filterRole }}</label>
        <select v-model="filterRole" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500 focus:bg-white dark:focus:bg-slate-900 dark:text-white transition-all cursor-pointer">
          <option value="">{{ tExt.allRoles }}</option>
          <option value="super_admin">SUPER_ADMIN</option>
          <option value="admin">ADMIN</option>
          <option value="staff">STAFF</option>
          <option value="cashier">CASHIER</option>
          <option value="warehouse">WAREHOUSE</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">⚡ {{ tExt.filterAction }}</label>
        <select v-model="filterAction" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500 focus:bg-white dark:focus:bg-slate-900 dark:text-white transition-all cursor-pointer">
          <option value="">{{ tExt.allActions }}</option>
          <option v-for="act in actionOptions" :key="act" :value="act">
            {{ getActionLabel(act) }}
          </option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">📅 {{ tExt.filterDate }}</label>
          <input v-model="filterDate" type="date" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs outline-none focus:border-blue-500 focus:bg-white dark:focus:bg-slate-900 dark:text-white transition-all font-mono" />
        </div>
        <button @click="resetFilters" class="px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-semibold transition-colors mt-6 cursor-pointer">
          {{ tExt.resetBtn }}
        </button>
      </div>
    </div>

    <!-- 日志表格 -->
    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xs border border-slate-200/80 dark:border-slate-700 overflow-hidden">
      <div class="px-6 py-3 bg-slate-50/50 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>{{ tExt.showing }} <strong class="text-slate-800 dark:text-slate-200">{{ filteredLogs.length }}</strong> / {{ tExt.total }} {{ logsList.length }} {{ tExt.records }}</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-700 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <th class="px-6 py-3 w-16">{{ tExt.colId }}</th>
              <th class="px-6 py-3">{{ tExt.colUser }}</th>
              <th class="px-6 py-3">{{ tExt.colRole }}</th>
              <th class="px-6 py-3">{{ tExt.colAction }}</th>
              <th class="px-6 py-3">{{ tExt.colDetails }}</th>
              <th class="px-6 py-3 text-right">{{ tExt.colTime }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700 text-xs">
            <tr v-for="log in paginatedLogs" :key="log.id" class="hover:bg-blue-50/30 dark:hover:bg-slate-700/50 transition-colors">
              <td class="px-6 py-4 font-mono text-slate-400 dark:text-slate-500">#{{ log.id }}</td>
              <td class="px-6 py-4 font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                {{ log.username }}
              </td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 rounded-lg font-bold text-[10px] border" :class="getRoleColorClass(log.role)">
                  {{ (log.role || '').toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4 font-mono font-semibold text-slate-700 dark:text-slate-300">
                <span class="px-2.5 py-1 rounded-md text-[11px] border" :class="getActionColorClass(log.action)">
                  {{ getActionLabel(log.action) }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-600 dark:text-slate-400 max-w-xs truncate" :title="log.details">
                {{ log.details }}
              </td>
              <td class="px-6 py-4 text-right font-mono text-slate-400 dark:text-slate-500">
                {{ log.created_at }}
              </td>
            </tr>
            <tr v-if="paginatedLogs.length === 0 && !loading">
              <td colspan="6" class="px-6 py-16 text-center text-slate-400 dark:text-slate-500 font-bold">
                <span class="text-3xl block mb-2">📭</span>
                {{ tExt.emptyData }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 🌟 新增：分页组件 -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50 dark:bg-slate-900 border-t border-slate-100 dark:border-slate-700 flex flex-wrap items-center justify-between gap-4 text-xs">
        <span class="text-slate-500 dark:text-slate-400 font-medium">
          显示第 <strong class="text-slate-800 dark:text-slate-200">{{ (currentPage - 1) * pageSize + 1 }}</strong> 到 <strong class="text-slate-800 dark:text-slate-200">{{ Math.min(currentPage * pageSize, filteredLogs.length) }}</strong> 条，共 <strong class="text-slate-800 dark:text-slate-200">{{ filteredLogs.length }}</strong> 条记录
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">跳转到</span>
            <input 
              type="number" 
              min="1" 
              :max="totalPages" 
              v-model.number="jumpPageInput" 
              @keyup.enter="handleJumpPage"
              class="w-12 text-center font-mono font-bold text-blue-600 dark:text-blue-400 bg-slate-50 dark:bg-slate-900 rounded-lg py-1 outline-none border border-slate-200 dark:border-slate-600 focus:border-blue-500 text-xs" 
            />
            <span class="text-slate-400 text-[11px]">/ {{ totalPages }} 页</span>
            <button 
              @click="handleJumpPage" 
              class="bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-800 text-blue-600 dark:text-blue-400 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]"
            >
              跳转
            </button>
          </div>

          <div class="flex items-center gap-1.5">
            <button 
              @click="currentPage--" 
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 font-semibold text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >
              上一页
            </button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700 dark:text-slate-300">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <button 
              @click="currentPage++" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 font-semibold text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 精美现代提示弹窗 -->
    <div v-if="warningModalVisible" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl max-w-sm w-full overflow-hidden border border-slate-100 dark:border-slate-700 p-6 space-y-5 text-center animate-in fade-in zoom-in-95 duration-150">
        <div class="w-12 h-12 rounded-2xl bg-amber-500 mx-auto flex items-center justify-center text-white shadow-lg shadow-amber-500/30 text-xl font-bold">
          ⚠️
        </div>
        <div class="space-y-1">
          <h3 class="font-bold text-base text-slate-900 dark:text-slate-100">{{ tExt.tipTitle }}</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{{ warningMessage }}</p>
        </div>
        <button @click="warningModalVisible = false" class="w-full py-3 bg-slate-900 dark:bg-slate-700 hover:bg-slate-800 dark:hover:bg-slate-600 text-white rounded-xl text-xs font-bold shadow-md transition-colors cursor-pointer">
          {{ t.common.confirm }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'

const { t, currentLang } = useI18n()
const logsList = ref([])
const loading = ref(false)

// 🌟 筛选条件状态
const filterUsername = ref('')
const filterRole = ref('')
const filterAction = ref('')
const filterDate = ref('')

// 🌟 分页状态
const currentPage = ref(1)
const pageSize = 10 // 审计日志一般行高较小，可以一页显示15条
const jumpPageInput = ref(1)

// 🌟 现代提示弹窗状态
const warningModalVisible = ref(false)
const warningMessage = ref('')

// 所有支持的动作代码列表，用于下拉框渲染
const actionOptions = [
  'CREATE_QUOTATION', 'CLIENT_REPAYMENT', 'UPDATE_STOCK', 'CREATE_PART', 'DELETE_PART',
  'CREATE_CLIENT', 'DELETE_CLIENT', 'CREATE_STAFF', 'DELETE_STAFF', 'RECEIVE_PURCHASE_ORDER', 'CREATE_PURCHASE_ORDER'
]

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '系统审计日志' : isEs ? 'Registros de Auditoría' : 'System Audit Logs',
    subtitle: isZh ? '实时记录每一次敏感操作，保障资金与数据安全' : isEs ? 'Registre operaciones sensibles, garantice seguridad' : 'Track sensitive operations to ensure security',
    exportBtn: isZh ? '导出 CSV' : isEs ? 'Exportar CSV' : 'Export CSV',
    filterUser: isZh ? '操作人' : isEs ? 'Usuario' : 'User',
    phUser: isZh ? '搜索用户名...' : isEs ? 'Buscar usuario...' : 'Search username...',
    filterRole: isZh ? '角色' : isEs ? 'Rol' : 'Role',
    allRoles: isZh ? '全部角色' : isEs ? 'Todos los Roles' : 'All Roles',
    filterAction: isZh ? '操作类型' : isEs ? 'Tipo de Acción' : 'Action Type',
    allActions: isZh ? '全部操作' : isEs ? 'Todas las Acciones' : 'All Actions',
    filterDate: isZh ? '日期' : isEs ? 'Fecha' : 'Date',
    resetBtn: isZh ? '重置' : isEs ? 'Limpiar' : 'Reset',
    showing: isZh ? '当前显示:' : isEs ? 'Mostrando:' : 'Showing:',
    total: isZh ? '总计' : isEs ? 'Total' : 'Total',
    records: isZh ? '条' : isEs ? 'registros' : 'records',
    colId: 'ID',
    colUser: isZh ? '操作人' : isEs ? 'Usuario' : 'User',
    colRole: isZh ? '角色' : isEs ? 'Rol' : 'Role',
    colAction: isZh ? '操作动作' : isEs ? 'Acción' : 'Action',
    colDetails: isZh ? '详情' : isEs ? 'Detalles' : 'Details',
    colTime: isZh ? '时间' : isEs ? 'Fecha' : 'Time',
    emptyData: isZh ? '暂无审计日志数据' : isEs ? 'No hay registros de auditoría' : 'No audit logs found',
    tipTitle: isZh ? '提示' : isEs ? 'Aviso' : 'Notice',
    unknownAction: isZh ? '未知操作' : isEs ? 'Acción Desconocida' : 'Unknown Action'
  }
})

// 🌟 将动作代码翻译成业务术语
const getActionLabel = (code) => {
  if (!code) return '-'
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'

  const dict = {
    'CREATE_QUOTATION': { zh: '🛒 开单挂账成交', es: 'Venta a Crédito', en: 'Credit Sale' },
    'CLIENT_REPAYMENT': { zh: '💰 客户还款销账', es: 'Cobro de Deuda', en: 'Client Repayment' },
    'UPDATE_STOCK': { zh: '📦 库存进出变动', es: 'Movimiento de Stock', en: 'Stock Movement' },
    'CREATE_PART': { zh: '➕ 新增配件商品', es: 'Nuevo Repuesto', en: 'Create Part' },
    'DELETE_PART': { zh: '🗑️ 删除配件商品', es: 'Eliminar Repuesto', en: 'Delete Part' },
    'CREATE_CLIENT': { zh: '👥 新增客户档案', es: 'Nuevo Cliente', en: 'Create Client' },
    'DELETE_CLIENT': { zh: '❌ 删除客户档案', es: 'Eliminar Cliente', en: 'Delete Client' },
    'UPDATE_CLIENT': { zh: '✏️ 修改客户档案', es: 'Editar Cliente', en: 'Update Client' }, // 补充了这个
    'CREATE_STAFF': { zh: '👨‍💼 新增员工账号', es: 'Nuevo Empleado', en: 'Create Staff' },
    'DELETE_STAFF': { zh: '🚫 删除员工账号', es: 'Eliminar Empleado', en: 'Delete Staff' },
    'RECEIVE_PURCHASE_ORDER': { zh: '📦 采购收货入库', es: 'Recepción de Compra', en: 'Receive PO' },
    'CREATE_PURCHASE_ORDER': { zh: '📝 创建采购单', es: 'Nueva Orden de Compra', en: 'Create PO' }
  }

  if (dict[code]) {
    return isZh ? dict[code].zh : isEs ? dict[code].es : dict[code].en
  }
  return code
}

// 动作标签配色
const getActionColorClass = (code) => {
  if (['CREATE_QUOTATION', 'RECEIVE_PURCHASE_ORDER', 'CREATE_PURCHASE_ORDER', 'CREATE_CLIENT', 'CREATE_PART'].includes(code)) {
    return 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800'
  }
  if (['DELETE_PART', 'DELETE_CLIENT', 'DELETE_STAFF'].includes(code)) {
    return 'bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800'
  }
  if (['UPDATE_STOCK', 'CLIENT_REPAYMENT', 'UPDATE_CLIENT'].includes(code)) {
    return 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800'
  }
  return 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700'
}

// 角色标签配色
const getRoleColorClass = (role) => {
  if (role === 'super_admin') return 'bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800'
  if (role === 'admin') return 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800'
  if (role === 'cashier') return 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800'
  return 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700'
}

const showWarning = (msg) => {
  warningMessage.value = msg
  warningModalVisible.value = true
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await apiFetch('/api/audit-logs')
    if (res.ok) {
      const resData = await res.json()
      if (Array.isArray(resData)) {
        logsList.value = resData
      } else if (resData && Array.isArray(resData.data)) {
        logsList.value = resData.data
      } else {
        logsList.value = []
      }
    }
  } catch (e) {
    console.error('获取审计日志失败:', e)
  } finally {
    loading.value = false
  }
}

// 🌟 一键导出当前筛选后的审计日志 (CSV)
const exportAuditLogsCsv = () => {
  if (filteredLogs.value.length === 0) {
    showWarning(t.value.messages?.exportEmptyError || '当前没有可导出的日志数据')
    return
  }

  let csvContent = "\uFEFF"
  csvContent += `${tExt.value.colId},${tExt.value.colUser},${tExt.value.colRole},${tExt.value.colAction},${tExt.value.colDetails},${tExt.value.colTime}\r\n`

  filteredLogs.value.forEach(log => {
    const detailsClean = `"${(log.details || '').replace(/"/g, '""')}"`
    const row = [
      log.id,
      log.username,
      log.role,
      getActionLabel(log.action),
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

// 🌟 分页计算属性
const totalPages = computed(() => {
  return Math.ceil(filteredLogs.value.length / pageSize) || 1
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredLogs.value.slice(start, start + pageSize)
})

// 🌟 跳转处理
const handleJumpPage = () => {
  let target = parseInt(jumpPageInput.value)
  if (isNaN(target)) return
  if (target < 1) target = 1
  if (target > totalPages.value) target = totalPages.value
  currentPage.value = target
  jumpPageInput.value = target
}

// 🌟 监听筛选条件变化，重置页码
watch([filterUsername, filterRole, filterAction, filterDate], () => {
  currentPage.value = 1
  jumpPageInput.value = 1
})

watch(currentPage, (val) => {
  jumpPageInput.value = val
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