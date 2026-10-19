<!-- src/components/StaffManagementView.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api' 
import ConfirmDialog from './ConfirmDialog.vue' 
import { useNotifications } from '../composables/useNotifications' 

const { t } = useI18n()
const { showSuccessModal } = useNotifications()
const staffList = ref([])

const permissionGroups = [
  {
    title: '💰 前台收银与开单 (POS & Checkout)',
    permissions: [
      { key: 'pos:access', label: '进入收银工作台' },
      { key: 'pos:checkout', label: '执行结账与出单' },
      { key: 'pos:hold', label: '挂单与取单操作' },
      { key: 'pos:discount', label: '特权打价与改价' }
    ]
  },
  {
    title: '📦 商品与库存管理 (Inventory & Parts)',
    permissions: [
      { key: 'parts:view', label: '查看商品库存' },
      { key: 'parts:manage', label: '新增/编辑商品档案' },
      { key: 'parts:import', label: 'CSV 批量导入导出' }
    ]
  },
  {
    title: '👥 客户与赊账管理 (Clients & Fiado)',
    permissions: [
      { key: 'clients:view', label: '查看客户名册' },
      { key: 'clients:manage', label: '新增与编辑客户' },
      { key: 'fiado:pay', label: 'Fiado 赊账还款核销' }
    ]
  },
  {
    title: '📄 报价单与采购 (Quotations & Procurement)',
    permissions: [
      { key: 'quotations:export', label: '下载与导出报价单 PDF' },
      { key: 'procurement:view', label: '采购与进货存单管理' }
    ]
  },
  {
    title: '📊 财务与报表 (Financial & Analytics)',
    permissions: [
      { key: 'financial:view', label: '查看财务利润大盘' },
      { key: 'shift:report', label: '今日班结 (Z-Report)' },
      { key: 'transactions:history', label: '查看历史流水与退货' }
    ]
  },
  {
    title: '⚙️ 系统设置与运维 (Settings & Security)',
    permissions: [
      { key: 'settings:manage', label: '系统参数与公司抬头配置' },
      { key: 'db:maintenance', label: '数据库清理与备份' },
      { key: 'users:manage', label: '员工账号与权限管理' }
    ]
  }
]

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

// 🌟 新增：判断当前分组是否已全选
const isGroupAllSelected = (groupPermissions) => {
  if (groupPermissions.length === 0) return false
  return groupPermissions.every(p => newStaff.value.permissions.includes(p.key))
}

// 🌟 重构：智能全选/取消全选
const toggleGroup = (groupPermissions) => {
  const allSelected = isGroupAllSelected(groupPermissions)
  let currentPerms = [...newStaff.value.permissions]
  
  if (allSelected) {
    // 如果已经全选，则清空该组
    const keysToRemove = groupPermissions.map(p => p.key)
    currentPerms = currentPerms.filter(k => !keysToRemove.includes(k))
  } else {
    // 如果没有全选，则全部加上
    groupPermissions.forEach(p => {
      if (!currentPerms.includes(p.key)) {
        currentPerms.push(p.key)
      }
    })
  }
  newStaff.value.permissions = currentPerms
}

// 🌟 新增：处理单个复选框变化
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
    errorMessage.value = t.value.errorRequired || '请填写账号和密码'
    return
  }

  try {
    const res = await apiFetch('/api/staff', {
      method: 'POST',
      body: JSON.stringify(newStaff.value)
    })
    
    if (res.ok) {
      const msg = `[${newStaff.value.username}] ${t.value.staffSuccessMsg || '员工创建成功！'}`
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
      errorMessage.value = err.detail || '创建失败'
    }
  } catch (e) {
    errorMessage.value = '服务器连接失败'
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
      showSuccessModal('🗑️ 员工账号已成功删除！')
      targetStaffForDelete.value = null
      fetchStaff()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 操作失败: ${err.detail || '未知错误'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 服务器连接异常！')
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
        <h2 class="font-bold text-lg text-slate-800">👥 {{ t.staffTitle || '员工账号与细粒度权限管理' }}</h2>
        <p class="text-xs text-slate-400 mt-0.5">{{ t.staffSub || '精准配置每个员工的操作权限，保障汽配店资金与库存安全' }}</p>
      </div>
    </div>

    <form @submit.prevent="handleCreateStaff" class="bg-white p-6 rounded-2xl shadow-xs border border-slate-100 space-y-5">
      <h3 class="font-bold text-sm text-slate-700 uppercase tracking-wider">➕ {{ t.staffAddTitle || '新增员工账号与权限勾选' }}</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staffUsernameLabel || '登录用户名' }}</label>
          <input 
            v-model="newStaff.username" 
            type="text" 
            autocomplete="username" 
            placeholder="carlos / maria" 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staffPasswordLabel || '登录密码' }}</label>
          <input 
            v-model="newStaff.password" 
            type="password" 
            autocomplete="new-password" 
            placeholder="••••••••" 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staffRoleLabel || '基础角色' }}</label>
          <select v-model="newStaff.role" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 cursor-pointer font-semibold">
            <option value="staff">Staff (普通店员)</option>
            <option value="cashier">Cashier (收银员)</option>
            <option value="warehouse">Warehouse (仓管员)</option>
          </select>
        </div>
      </div>

      <div class="space-y-3 pt-2 border-t border-slate-100">
        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider">🛡️ 细粒度功能权限勾选 (Granular Permissions)</label>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="group in permissionGroups" :key="group.title" class="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 space-y-3">
            <div class="flex items-center justify-between border-b border-slate-200/60 pb-2">
              <span class="text-xs font-black text-slate-800">{{ group.title }}</span>
              <div class="space-x-2 text-[10px]">
                <!-- 🌟 智能全选/取消全选按钮 -->
                <button 
                  type="button" 
                  @click="toggleGroup(group.permissions)" 
                  class="text-blue-600 hover:underline font-bold"
                >
                  {{ isGroupAllSelected(group.permissions) ? '取消全选' : '全选' }}
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
          {{ t.staffCreateBtn || '保存并创建员工账号' }}
        </button>
      </div>
    </form>

    <div class="bg-white rounded-2xl shadow-xs border border-slate-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-slate-100">
        <h3 class="font-bold text-sm text-slate-700">{{ t.staffListTitle || '已有员工账号与权限概览' }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase">
              <th class="px-6 py-3">{{ t.staffTableId || 'ID' }}</th>
              <th class="px-6 py-3">{{ t.staffTableUser || '用户名' }}</th>
              <th class="px-6 py-3">{{ t.staffTableRole || '角色' }}</th>
              <th class="px-6 py-3">已授权限预览</th>
              <th class="px-6 py-3">{{ t.staffTableTime || '创建时间' }}</th>
              <th class="px-6 py-3 text-right">{{ t.staffTableAction || '操作' }}</th>
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
                  {{ s.permissions ? s.permissions.length : 0 }} 项细粒度权限
                </span>
              </td>
              <td class="px-6 py-4 font-mono text-slate-500">{{ s.created_at }}</td>
              <td class="px-6 py-4 text-right">
                <button @click="openDeleteStaffModal(s)" class="px-3 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-lg font-semibold transition-colors cursor-pointer">
                  {{ t.staffDeleteBtn || '删除' }}
                </button>
              </td>
            </tr>
            <tr v-if="staffList.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-slate-400">{{ t.staffEmpty || '暂无员工账号' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <ConfirmDialog
      :visible="deleteStaffModalVisible"
      overlay-class="bg-slate-900/40"
      title="确认删除员工账号"
      :message="targetStaffForDelete ? `确定要永久删除员工 [${targetStaffForDelete.username}] 的账号吗？` : '确定要删除该员工账号吗？'"
      cancel-text="取消"
      confirm-text="确认删除"
      @cancel="deleteStaffModalVisible = false"
      @confirm="confirmDeleteStaff"
    />
  </div>
</template>