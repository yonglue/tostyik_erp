<!-- src/components/StaffManagementView.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api' // 引入咱们封装好的安全请求工具

const { t } = useI18n()
const staffList = ref([])
const newStaff = ref({ username: '', password: '', role: 'staff' })
const errorMessage = ref('')
const successMessage = ref('')

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
      successMessage.value = `[${newStaff.value.username}] ${t.value.staffSuccessMsg}`
      newStaff.value = { username: '', password: '', role: 'staff' }
      fetchStaff()
    } else {
      const err = await res.json()
      errorMessage.value = err.detail || '创建失败'
    }
  } catch (e) {
    errorMessage.value = '服务器连接失败'
  }
}

const deleteStaff = async (id) => {
  if (!confirm(t.value.staffDeleteConfirm)) return
  try {
    const res = await apiFetch(`/api/staff/${id}`, { method: 'DELETE' })
    if (res.ok) {
      fetchStaff()
    } else {
      const err = await res.json()
      alert(err.detail || '操作失败')
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchStaff()
})
</script>

<template>
  <div class="space-y-6 max-w-4xl mx-auto">
    <!-- 头部标题 -->
    <div class="bg-white p-6 rounded-2xl shadow-xs border border-slate-100 flex items-center justify-between">
      <div>
        <h2 class="font-bold text-lg text-slate-800">👥 {{ t.staffTitle }}</h2>
        <p class="text-xs text-slate-400 mt-0.5">{{ t.staffSub }}</p>
      </div>
    </div>

    <!-- 创建员工表单 -->
    <div class="bg-white p-6 rounded-2xl shadow-xs border border-slate-100 space-y-4">
      <h3 class="font-bold text-sm text-slate-700 uppercase tracking-wider">{{ t.staffAddTitle }}</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staffUsernameLabel }}</label>
          <input v-model="newStaff.username" type="text" placeholder="carlos / maria" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staffPasswordLabel }}</label>
          <input v-model="newStaff.password" type="password" placeholder="••••••••" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.staffRoleLabel }}</label>
          <select v-model="newStaff.role" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 cursor-pointer">
            <option value="staff">Staff (普通店员/开单)</option>
            <option value="cashier">Cashier (收银员)</option>
            <option value="warehouse">Warehouse (仓管员)</option>
          </select>
        </div>
      </div>
      <div class="flex items-center justify-between pt-2">
        <div>
          <p v-if="errorMessage" class="text-xs font-semibold text-rose-600">{{ errorMessage }}</p>
          <p v-if="successMessage" class="text-xs font-semibold text-emerald-600">{{ successMessage }}</p>
        </div>
        <button @click="handleCreateStaff" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs shadow-md shadow-blue-500/20 transition-all">
          {{ t.staffCreateBtn }}
        </button>
      </div>
    </div>

    <!-- 员工列表展示 -->
    <div class="bg-white rounded-2xl shadow-xs border border-slate-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-slate-100">
        <h3 class="font-bold text-sm text-slate-700">{{ t.staffListTitle }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase">
              <th class="px-6 py-3">{{ t.staffTableId }}</th>
              <th class="px-6 py-3">{{ t.staffTableUser }}</th>
              <th class="px-6 py-3">{{ t.staffTableRole }}</th>
              <th class="px-6 py-3">{{ t.staffTableTime }}</th>
              <th class="px-6 py-3 text-right">{{ t.staffTableAction }}</th>
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
              <td class="px-6 py-4 font-mono text-slate-500">{{ s.created_at }}</td>
              <td class="px-6 py-4 text-right">
                <button @click="deleteStaff(s.id)" class="px-3 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-lg font-semibold transition-colors">
                  {{ t.staffDeleteBtn }}
                </button>
              </td>
            </tr>
            <tr v-if="staffList.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-slate-400">{{ t.staffEmpty }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>