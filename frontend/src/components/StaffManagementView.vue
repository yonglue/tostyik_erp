<!-- src/components/StaffManagementView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-12">
    
    <!-- 顶部标题栏 -->
    <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-xs border border-slate-200/80 dark:border-slate-700 flex items-center justify-between transition-colors">
      <div>
        <h2 class="font-bold text-lg text-slate-800 dark:text-slate-200 flex items-center gap-2">
          <span>👥</span> {{ t.staff.title }}
        </h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ t.staff.subtitle }}</p>
      </div>
    </div>

    <!-- 新增员工表单 -->
    <form @submit.prevent="handleCreateStaff" class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-xs border border-slate-200/80 dark:border-slate-700 space-y-6 transition-colors">
      <h3 class="font-bold text-sm text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2 border-b border-slate-100 dark:border-slate-700 pb-3">
        <span>➕</span> {{ t.staff.addTitle }}
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div>
          <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">{{ t.staff.usernameLabel }}</label>
          <input 
            v-model="newStaff.username" 
            type="text" 
            autocomplete="off" 
            :placeholder="tExt.phUsername" 
            class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:bg-white dark:focus:bg-slate-900 transition-all font-mono placeholder:text-slate-400 dark:placeholder:text-slate-500" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">{{ t.staff.passwordLabel }}</label>
          <input 
            v-model="newStaff.password" 
            type="password" 
            autocomplete="new-password" 
            placeholder="••••••••" 
            class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:bg-white dark:focus:bg-slate-900 transition-all font-mono placeholder:text-slate-400 dark:placeholder:text-slate-500" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">{{ t.staff.roleLabel }}</label>
          <select v-model="newStaff.role" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:bg-white dark:focus:bg-slate-900 transition-all cursor-pointer font-semibold">
            <option v-for="role in roleOptions" :key="role.value" :value="role.value">
              {{ role.label }}
            </option>
          </select>
        </div>
      </div>

      <!-- 权限矩阵 -->
      <div class="space-y-4 pt-2">
        <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <span>🛡️</span> {{ t.staff.colPermissions }}
        </label>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div v-for="group in permissionGroups" :key="group.title" class="bg-slate-50/50 dark:bg-slate-900/50 border border-slate-200/80 dark:border-slate-700 rounded-2xl p-4 space-y-3 shadow-2xs hover:shadow-sm transition-all">
            <div class="flex items-center justify-between border-b border-slate-200/60 dark:border-slate-700 pb-2">
              <span class="text-xs font-black text-slate-800 dark:text-slate-200">{{ group.title }}</span>
              <button 
                type="button" 
                @click="toggleGroup(group.permissions)" 
                class="text-[10px] text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline font-bold cursor-pointer transition-colors"
              >
                {{ isGroupAllSelected(group.permissions) ? t.common.clearAll : t.common.selectAll }}
              </button>
            </div>
            <div class="space-y-2.5">
              <label 
                v-for="p in group.permissions" 
                :key="p.key" 
                class="flex items-start gap-2.5 text-xs text-slate-700 dark:text-slate-300 cursor-pointer select-none group"
              >
                <input 
                  type="checkbox" 
                  :checked="newStaff.permissions.includes(p.key)"
                  @change="(e) => handleCheckboxChange(p.key, e.target.checked)"
                  class="mt-0.5 rounded border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer transition-all" 
                />
                <span class="font-medium group-hover:text-blue-700 dark:group-hover:text-blue-400 transition-colors leading-tight">{{ p.label }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- 提交操作 -->
      <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-700">
        <div>
          <p v-if="errorMessage" class="text-xs font-semibold text-rose-600 dark:text-rose-400 flex items-center gap-1">
            <span>❌</span> {{ errorMessage }}
          </p>
          <p v-if="successMessage" class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
            <span>✅</span> {{ successMessage }}
          </p>
        </div>
        <button type="submit" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs shadow-md shadow-blue-500/20 transition-all cursor-pointer flex items-center gap-2">
          <span>💾</span> {{ t.staff.createBtn }}
        </button>
      </div>
    </form>

    <!-- 员工列表 -->
    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xs border border-slate-200/80 dark:border-slate-700 overflow-hidden transition-colors">
      <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50">
        <h3 class="font-bold text-sm text-slate-700 dark:text-slate-300">{{ t.staff.listTitle }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-700 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <th class="px-6 py-3 w-16">{{ t.staff.colId }}</th>
              <th class="px-6 py-3">{{ t.staff.colUser }}</th>
              <th class="px-6 py-3">{{ t.staff.colRole }}</th>
              <th class="px-6 py-3">{{ t.staff.colPermissions }}</th>
              <th class="px-6 py-3">{{ t.staff.colTime }}</th>
              <th class="px-6 py-3 text-right">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700 text-xs">
            <tr v-for="s in staffList" :key="s.id" class="hover:bg-blue-50/30 dark:hover:bg-slate-700/50 transition-colors">
              <td class="px-6 py-4 font-mono text-slate-400 dark:text-slate-500">#{{ s.id }}</td>
              <td class="px-6 py-4 font-bold text-slate-800 dark:text-slate-200 text-sm">{{ s.username }}</td>
              <td class="px-6 py-4">
                <span 
                  class="px-2.5 py-1 rounded-lg font-bold text-[10px] border"
                  :class="getRoleColorClass(s.role)"
                >
                  {{ getRoleLabel(s.role) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center gap-1 text-[11px] font-mono font-semibold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-100 dark:border-indigo-800 px-2.5 py-1 rounded-md">
                  <span>🔑</span> {{ s.permissions ? s.permissions.length : 0 }} {{ t.staff.permissionCount }}
                </span>
              </td>
              <td class="px-6 py-4 font-mono text-slate-500 dark:text-slate-400">{{ s.created_at }}</td>
              <td class="px-6 py-4 text-right">
                <button @click="openDeleteStaffModal(s)" class="px-3 py-1.5 bg-rose-50 dark:bg-rose-900/30 hover:bg-rose-100 dark:hover:bg-rose-900/50 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-800 rounded-lg font-bold transition-colors cursor-pointer">
                  {{ t.common.delete }}
                </button>
              </td>
            </tr>
            <tr v-if="staffList.length === 0">
              <td colspan="6" class="px-6 py-12 text-center text-slate-400 dark:text-slate-500">
                <span class="text-3xl block mb-2">📭</span>
                {{ t.staff.empty }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <ConfirmDialog
      :visible="deleteStaffModalVisible"
      overlay-class="bg-slate-900/40"
      :title="t.common.confirm"
      :message="targetStaffForDelete ? `${t.messages.confirmDeleteStaff} [${targetStaffForDelete.username}]` : t.messages.confirmDeleteStaff"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="deleteStaffModalVisible = false"
      @confirm="confirmDeleteStaff"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api' 
import ConfirmDialog from './ConfirmDialog.vue' 
import { useNotifications } from '../composables/useNotifications' 

const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const staffList = ref([])

// 局部翻译字典（补充专业性措辞）
const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    phUsername: isZh ? '例如: maria' : isEs ? 'Ej: maria' : 'E.g. maria'
  }
})

/**
 * 🌟 权限矩阵定义：专业的行业术语映射
 */
const permissionGroups = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'

  return [
    {
      title: t.value.staff.permGroupPos || 'POS & Caja',
      permissions: [
        { key: 'pos:access', label: isZh ? '访问收银台' : isEs ? 'Acceder a Caja' : 'Access POS' },
        { key: 'pos:checkout', label: isZh ? '结账与开单' : isEs ? 'Cobrar y Facturar' : 'Checkout & Billing' },
        { key: 'pos:refund', label: isZh ? '执行退货操作' : isEs ? 'Procesar Devoluciones' : 'Process Refunds' },
        { key: 'pos:hold', label: isZh ? '云端挂单/取单' : isEs ? 'Retener/Recuperar Pedidos' : 'Hold & Recall Orders' },
        { key: 'pos:discount', label: isZh ? '折扣与改价权限' : isEs ? 'Descuentos y Cambios de Precio' : 'Discounts & Repricing' }
      ]
    },
    {
      title: t.value.staff.permGroupInventory || 'Inventario',
      permissions: [
        { key: 'parts:view', label: isZh ? '查看商品库存' : isEs ? 'Ver Inventario' : 'View Inventory' },
        { key: 'parts:manage', label: isZh ? '编辑商品档案' : isEs ? 'Editar Repuestos' : 'Manage Parts' },
        { key: 'parts:import', label: isZh ? '导入/导出 CSV' : isEs ? 'Importar/Exportar CSV' : 'Import/Export CSV' }
      ]
    },
    {
      title: t.value.staff.permGroupClients || 'Clientes',
      permissions: [
        { key: 'clients:view', label: isZh ? '查看客户资料' : isEs ? 'Ver Clientes' : 'View Clients' },
        { key: 'clients:manage', label: isZh ? '新增/编辑客户' : isEs ? 'Editar Clientes' : 'Manage Clients' },
        { key: 'fiado:pay', label: isZh ? '赊账还款核销' : isEs ? 'Cobrar Crédito (Fiado)' : 'Process Credit Payments' }
      ]
    },
    {
      title: t.value.staff.permGroupQuotations || 'Cotizaciones',
      permissions: [
        { key: 'quotations:export', label: isZh ? '导出报价单 PDF' : isEs ? 'Exportar PDF Cotizaciones' : 'Export Quotation PDF' },
        { key: 'procurement:view', label: isZh ? '采购单管理' : isEs ? 'Gestión de Compras' : 'Manage Purchase Orders' }
      ]
    },
    {
      title: t.value.staff.permGroupFinancial || 'Finanzas',
      permissions: [
        { key: 'financial:view', label: isZh ? '查看财务利润大盘' : isEs ? 'Ver Finanzas' : 'View Financials' },
        { key: 'shift:report', label: isZh ? '收银班结 (Z-Report)' : isEs ? 'Cierre de Caja (Z)' : 'Shift Report (Z)' },
        { key: 'transactions:history', label: isZh ? '历史流水与退货' : isEs ? 'Historial de Movimientos' : 'Transaction History' }
      ]
    },
    {
      title: t.value.staff.permGroupSettings || 'Sistema',
      permissions: [
        { key: 'settings:manage', label: isZh ? '系统参数与公司配置' : isEs ? 'Configuración de Empresa' : 'Company Settings' },
        { key: 'db:maintenance', label: isZh ? '数据库备份维护' : isEs ? 'Mantenimiento de DB' : 'DB Maintenance' },
        { key: 'users:manage', label: isZh ? '员工账号与权限' : isEs ? 'Gestión de Personal' : 'Staff Management' }
      ]
    }
  ]
})

// 🌟 角色下拉框彻底去英文混排，采用专业名称
const roleOptions = computed(() => [
  { value: 'staff', label: currentLang.value === 'zh' ? '普通员工' : currentLang.value === 'es' ? 'Empleado' : 'Staff' },
  { value: 'cashier', label: currentLang.value === 'zh' ? '收银员' : currentLang.value === 'es' ? 'Cajero' : 'Cashier' },
  { value: 'warehouse', label: currentLang.value === 'zh' ? '仓管员' : currentLang.value === 'es' ? 'Almacén' : 'Warehouse' },
  { value: 'manager', label: currentLang.value === 'zh' ? '店长' : currentLang.value === 'es' ? 'Gerente' : 'Manager' }
])

const getRoleLabel = (roleVal) => {
  const role = roleOptions.value.find(r => r.value === roleVal)
  return role ? role.label : roleVal.toUpperCase()
}

const getRoleColorClass = (roleVal) => {
  if (roleVal === 'cashier') return 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800'
  if (roleVal === 'warehouse') return 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800'
  if (roleVal === 'manager') return 'bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800'
  return 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800'
}

const newStaff = ref({ 
  username: '', 
  password: '', 
  role: 'staff',
  permissions: ['pos:access', 'pos:checkout', 'parts:view'] 
})

const errorMessage = ref('')
const successMessage = ref('')

const deleteStaffModalVisible = ref(false)
const targetStaffForDelete = ref(null)

const fetchStaff = async () => {
  try {
    const res = await apiFetch('/api/staff')
    if (res.ok) {
      staffList.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

const isGroupAllSelected = (groupPermissions) => {
  if (groupPermissions.length === 0) return false
  return groupPermissions.every(p => newStaff.value.permissions.includes(p.key))
}

const toggleGroup = (groupPermissions) => {
  const allSelected = isGroupAllSelected(groupPermissions)
  let currentPerms = [...newStaff.value.permissions]
  
  if (allSelected) {
    const keysToRemove = groupPermissions.map(p => p.key)
    currentPerms = currentPerms.filter(k => !keysToRemove.includes(k))
  } else {
    groupPermissions.forEach(p => {
      if (!currentPerms.includes(p.key)) {
        currentPerms.push(p.key)
      }
    })
  }
  newStaff.value.permissions = currentPerms
}

const handleCheckboxChange = (key, checked) => {
  let perms = [...newStaff.value.permissions]
  if (checked) {
    if (!perms.includes(key)) perms.push(key)
  } else {
    perms = perms.filter(k => k !== key)
  }
  newStaff.value.permissions = perms
}

const handleCreateStaff = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  if (!newStaff.value.username || !newStaff.value.password) {
    errorMessage.value = t.value.messages.errorRequired
    return
  }

  try {
    const res = await apiFetch('/api/staff', {
      method: 'POST',
      body: JSON.stringify(newStaff.value)
    })
    
    if (res.ok) {
      const msg = `[${newStaff.value.username}] ${t.value.messages.staffSuccessMsg}`
      successMessage.value = msg
      showSuccessModal(`🎉 ${msg}`)
      newStaff.value = { 
        username: '', 
        password: '', 
        role: 'staff', 
        permissions: ['pos:access', 'pos:checkout', 'parts:view'] 
      }
      fetchStaff()
    } else {
      const err = await res.json()
      errorMessage.value = err.detail || t.value.common.error
    }
  } catch (e) {
    errorMessage.value = t.value.common.error
  }
}

const openDeleteStaffModal = (staff) => {
  targetStaffForDelete.value = staff
  deleteStaffModalVisible.value = true
}

const confirmDeleteStaff = async () => {
  if (!targetStaffForDelete.value) return
  try {
    const res = await apiFetch(`/api/staff/${targetStaffForDelete.value.id}`, { method: 'DELETE' })
    if (res.ok) {
      deleteStaffModalVisible.value = false
      showSuccessModal('🗑️ ' + t.value.common.success)
      targetStaffForDelete.value = null
      fetchStaff()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ ${t.value.common.error}: ${err.detail || 'Unknown'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ ' + t.value.common.error)
  }
}

onMounted(() => {
  fetchStaff()
})
</script>
