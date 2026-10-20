<!-- src/components/StaffManagementView.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api' 
import ConfirmDialog from './ConfirmDialog.vue' 
import { useNotifications } from '../composables/useNotifications' 

const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const staffList = ref([])

/**
 * 🌟 动态权限分组及标签映射
 * 使用 computed 确保当用户切换语言时，标题和所有细粒度权限标签实时响应更新
 */
const permissionGroups = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'

  return [
    {
      title: t.value.staff.permGroupPos,
      permissions: [
        { key: 'pos:access', label: isZh ? '进入收银工作台' : isEs ? 'Acceder a Caja' : 'Access POS' },
        { key: 'pos:checkout', label: isZh ? '执行结账与出单' : isEs ? 'Cobrar y Emitir' : 'Checkout & Bill' },
        { key: 'pos:refund', label: isZh ? '执行退货' : isEs ? 'Procesar Devoluciones' : 'Process Refunds' },
        { key: 'pos:hold', label: isZh ? '挂单与取单操作' : isEs ? 'Pausar y Recuperar' : 'Hold & Recall' },
        { key: 'pos:discount', label: isZh ? '特权打价与改价' : isEs ? 'Descuentos y Precios' : 'Discount & Reprice' }
      ]
    },
    {
      title: t.value.staff.permGroupInventory,
      permissions: [
        { key: 'parts:view', label: isZh ? '查看商品库存' : isEs ? 'Ver Inventario' : 'View Inventory' },
        { key: 'parts:manage', label: isZh ? '新增/编辑商品档案' : isEs ? 'Crear/Editar Repuesto' : 'Manage Parts' },
        { key: 'parts:import', label: isZh ? 'CSV 批量导入导出' : isEs ? 'Importar/Exportar CSV' : 'Import/Export CSV' }
      ]
    },
    {
      title: t.value.staff.permGroupClients,
      permissions: [
        { key: 'clients:view', label: isZh ? '查看客户名册' : isEs ? 'Ver Clientes' : 'View Clients' },
        { key: 'clients:manage', label: isZh ? '新增与编辑客户' : isEs ? 'Crear/Editar Cliente' : 'Manage Clients' },
        { key: 'fiado:pay', label: isZh ? 'Fiado 赊账还款核销' : isEs ? 'Cobrar Fiado' : 'Fiado Repayment' }
      ]
    },
    {
      title: t.value.staff.permGroupQuotations,
      permissions: [
        { key: 'quotations:export', label: isZh ? '下载与导出报价单 PDF' : isEs ? 'Exportar Cotizaciones PDF' : 'Export Quotations PDF' },
        { key: 'procurement:view', label: isZh ? '采购与进货存单管理' : isEs ? 'Gestión de Compras' : 'Procurement Mgmt' }
      ]
    },
    {
      title: t.value.staff.permGroupFinancial,
      permissions: [
        { key: 'financial:view', label: isZh ? '查看财务利润大盘' : isEs ? 'Ver Finanzas' : 'View Financials' },
        { key: 'shift:report', label: isZh ? '今日班结 (Z-Report)' : isEs ? 'Cierre de Caja (Z)' : 'Shift Report (Z)' },
        { key: 'transactions:history', label: isZh ? '查看历史流水与退货' : isEs ? 'Historial y Devoluciones' : 'History & Returns' }
      ]
    },
    {
      title: t.value.staff.permGroupSettings,
      permissions: [
        { key: 'settings:manage', label: isZh ? '系统参数与公司抬头配置' : isEs ? 'Configuración de Empresa' : 'Company Settings' },
        { key: 'db:maintenance', label: isZh ? '数据库清理与备份' : isEs ? 'Limpieza y Respaldo DB' : 'DB Maintenance' },
        { key: 'users:manage', label: isZh ? '员工账号与权限管理' : isEs ? 'Gestión de Personal' : 'Staff Mgmt' }
      ]
    }
  ]
})

// 🌟 角色下拉框的多语言映射
const roleOptions = computed(() => [
  { value: 'staff', label: currentLang.value === 'zh' ? 'Staff (普通店员)' : currentLang.value === 'es' ? 'Staff (Vendedor)' : 'Staff' },
  { value: 'cashier', label: currentLang.value === 'zh' ? 'Cashier (收银员)' : currentLang.value === 'es' ? 'Cashier (Cajero)' : 'Cashier' },
  { value: 'warehouse', label: currentLang.value === 'zh' ? 'Warehouse (仓管员)' : currentLang.value === 'es' ? 'Warehouse (Almacén)' : 'Warehouse' }
])

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
    // 🌟 使用新的 i18n 字典键值
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

<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-12">
    <div class="bg-white p-6 rounded-2xl shadow-xs border border-slate-100 flex items-center justify-between">
      <div>
        <h2 class="font-bold text-lg text-slate-800">👥 {{ t.staff.title }}</h2>
        <p class="text-xs text-slate-400 mt-0.5">{{ t.staff.subtitle }}</p>
      </div>
    </div>

    <form @submit.prevent="handleCreateStaff" class="bg-white p-6 rounded-2xl shadow-xs border border-slate-100 space-y-5">
      <h3 class="font-bold text-sm text-slate-700 uppercase tracking-wider">➕ {{ t.staff.addTitle }}</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staff.usernameLabel }}</label>
          <input 
            v-model="newStaff.username" 
            type="text" 
            autocomplete="username" 
            placeholder="carlos / maria" 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staff.passwordLabel }}</label>
          <input 
            v-model="newStaff.password" 
            type="password" 
            autocomplete="new-password" 
            placeholder="••••••••" 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staff.roleLabel }}</label>
          <select v-model="newStaff.role" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 cursor-pointer font-semibold">
            <option v-for="role in roleOptions" :key="role.value" :value="role.value">
              {{ role.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="space-y-3 pt-2 border-t border-slate-100">
        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider">🛡️ {{ t.staff.colPermissions }}</label>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="group in permissionGroups" :key="group.title" class="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 space-y-3">
            <div class="flex items-center justify-between border-b border-slate-200/60 pb-2">
              <span class="text-xs font-black text-slate-800">{{ group.title }}</span>
              <div class="space-x-2 text-[10px]">
                <button 
                  type="button" 
                  @click="toggleGroup(group.permissions)" 
                  class="text-blue-600 hover:underline font-bold"
                >
                  {{ isGroupAllSelected(group.permissions) ? t.common.clearAll : t.common.selectAll }}
                </button>
              </div>
            </div>
            <div class="space-y-2">
              <label v-for="p in group.permissions" :key="p.key" class="flex items-center gap-2.5 text-xs text-slate-700 cursor-pointer select-none hover:text-slate-900">
                <input 
                  type="checkbox" 
                  :checked="newStaff.permissions.includes(p.key)"
                  @change="(e) => handleCheckboxChange(p.key, e.target.checked)"
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
                <span class="font-medium">{{ p.label }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-3 border-t border-slate-100">
        <div>
          <p v-if="errorMessage" class="text-xs font-semibold text-rose-600">❌ {{ errorMessage }}</p>
          <p v-if="successMessage" class="text-xs font-semibold text-emerald-600">✅ {{ successMessage }}</p>
        </div>
        <button type="submit" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs shadow-md shadow-blue-500/20 transition-all cursor-pointer">
          {{ t.staff.createBtn }}
        </button>
      </div>
    </form>

    <div class="bg-white rounded-2xl shadow-xs border border-slate-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-slate-100">
        <h3 class="font-bold text-sm text-slate-700">{{ t.staff.listTitle }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase">
              <th class="px-6 py-3">{{ t.staff.colId }}</th>
              <th class="px-6 py-3">{{ t.staff.colUser }}</th>
              <th class="px-6 py-3">{{ t.staff.colRole }}</th>
              <th class="px-6 py-3">{{ t.staff.colPermissions }}</th>
              <th class="px-6 py-3">{{ t.staff.colTime }}</th>
              <th class="px-6 py-3 text-right">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-xs">
            <tr v-for="s in staffList" :key="s.id" class="hover:bg-slate-50/50">
              <td class="px-6 py-4 font-mono text-slate-400">#{{ s.id }}</td>
              <td class="px-6 py-4 font-bold text-slate-800">{{ s.username }}</td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 rounded-lg font-semibold text-[10px]" :class="s.role === 'cashier' ? 'bg-amber-50 text-amber-600' : 'bg-blue-50 text-blue-600'">
                  {{ s.role.toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span class="text-[11px] font-mono text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
                  {{ s.permissions ? s.permissions.length : 0 }} {{ t.staff.permissionCount }}
                </span>
              </td>
              <td class="px-6 py-4 font-mono text-slate-500">{{ s.created_at }}</td>
              <td class="px-6 py-4 text-right">
                <button @click="openDeleteStaffModal(s)" class="px-3 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-lg font-semibold transition-colors cursor-pointer">
                  {{ t.common.delete }}
                </button>
              </td>
            </tr>
            <tr v-if="staffList.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-slate-400">{{ t.staff.empty }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

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