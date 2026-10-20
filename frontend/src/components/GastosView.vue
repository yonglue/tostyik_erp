<!-- src/components/GastosView.vue -->
<template>
  <div class="space-y-6">
    <!-- 顶部操作栏 -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-900">💸 日常开支管理 (Gastos)</h2>
        <p class="text-xs text-slate-500 mt-1">记录店铺租金、工资、水电等日常支出，支撑净利润核算。</p>
      </div>
      <div class="flex items-center gap-3">
        <!-- 月份筛选 -->
        <input 
          type="month" 
          v-model="filterMonth" 
          class="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-4 py-2.5 outline-none focus:border-blue-500 transition-all cursor-pointer"
        />
        <button @click="fetchExpenses" class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all">
          🔄 刷新
        </button>
        <button @click="openAddModal" class="flex items-center justify-center gap-2 bg-rose-600 hover:bg-rose-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md transition-all">
          ➕ 记一笔支出
        </button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-4">支出日期</th>
              <th class="py-3.5 px-4">分类</th>
              <th class="py-3.5 px-4">详细说明</th>
              <th class="py-3.5 px-4">金额</th>
              <th class="py-3.5 px-4">折合 USD</th>
              <th class="py-3.5 px-4">支付方式</th>
              <th class="py-3.5 px-4">经办人</th>
              <th class="py-3.5 px-4 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="item in filteredExpenses" :key="item.id" class="hover:bg-rose-50/30 transition-colors">
              <td class="py-4 px-4 font-mono font-bold text-slate-700">{{ item.expense_date }}</td>
              <td class="py-4 px-4">
                <span class="bg-rose-50 text-rose-700 border border-rose-200/60 px-2.5 py-1 rounded-lg text-xs font-bold">
                  {{ item.category }}
                </span>
              </td>
              <td class="py-4 px-4 font-medium text-slate-900">{{ item.description || '-' }}</td>
              <td class="py-4 px-4 font-mono font-black" :class="item.currency === 'USD' ? 'text-emerald-600' : 'text-blue-600'">
                {{ item.currency === 'USD' ? '$' : 'Bs.' }} {{ Number(item.amount).toFixed(2) }}
              </td>
              <td class="py-4 px-4 font-mono font-bold text-slate-500">
                $ {{ (item.currency === 'USD' ? item.amount : item.amount / item.exchange_rate).toFixed(2) }}
              </td>
              <td class="py-4 px-4 text-xs font-semibold text-slate-500">
                {{ item.payment_method }}
              </td>
              <td class="py-4 px-4 text-xs text-slate-500">
                {{ item.created_by }}
              </td>
              <td class="py-4 px-4 text-center">
                <div class="inline-flex items-center justify-center gap-2">
                  <button @click="openEditModal(item)" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1 rounded-lg font-semibold transition-colors">编辑</button>
                  <button @click="confirmDelete(item.id)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1 rounded-lg font-semibold transition-colors">删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredExpenses.length === 0">
              <td colspan="8" class="py-16 text-center text-slate-400 text-sm">
                <span class="text-4xl block mb-3">📭</span>
                暂无符合条件的支出记录
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="modalVisible" @click.self="modalVisible = false" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 transition-all">
      <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="font-bold text-slate-800 text-base">{{ isEditing ? '编辑支出记录' : '新增日常开支' }}</h3>
          <button @click="modalVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold">✕</button>
        </div>

        <form @submit.prevent="saveExpense" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">支出分类</label>
              <select v-model="formData.category" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500 cursor-pointer">
                <option value="房租 (Alquiler)">房租 (Alquiler)</option>
                <option value="员工工资 (Nómina)">员工工资 (Nómina)</option>
                <option value="水电费 (Servicios)">水电费 (Servicios)</option>
                <option value="运输/物流 (Flete)">运输/物流 (Flete)</option>
                <option value="办公/杂费 (Varios)">办公/杂费 (Varios)</option>
                <option value="税费 (Impuestos)">税费 (Impuestos)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">支出日期</label>
              <input v-model="formData.expense_date" type="date" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">详细说明</label>
            <input v-model="formData.description" type="text" placeholder="例如：10月份店铺租金" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">金额</label>
              <input v-model.number="formData.amount" type="number" step="0.01" min="0" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-mono font-bold outline-none focus:border-rose-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">币种</label>
              <select v-model="formData.currency" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500 cursor-pointer">
                <option value="USD">美元 (USD)</option>
                <option value="BS">玻利瓦尔 (Bs.)</option>
              </select>
            </div>
          </div>

          <div v-if="formData.currency === 'BS'" class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">当前汇率 (Bs/USD)</label>
              <input v-model.number="formData.exchange_rate" type="number" step="0.01" min="0" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-mono font-bold outline-none focus:border-rose-500" />
            </div>
            <div class="flex items-end pb-3">
              <span class="text-xs text-slate-500 font-bold">折合美元: ${{ (formData.amount / formData.exchange_rate || 0).toFixed(2) }}</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">支付方式</label>
              <select v-model="formData.payment_method" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500 cursor-pointer">
                <option value="Cash_USD">现金 (美元)</option>
                <option value="Cash_BS">现金 (Bs.)</option>
                <option value="Pago_Movil">Pago Móvil</option>
                <option value="Card_POS">刷卡 (POS)</option>
                <option value="Bank_Transfer">银行转账</option>
                <option value="Zelle">Zelle</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">经办人</label>
              <input v-model="formData.created_by" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500" />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="modalVisible = false" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors">取消</button>
            <button type="submit" class="px-6 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-md transition-all">保存记录</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import { useAuth } from '../composables/useAuth'

const { showSuccessModal } = useNotifications()
const { currentUserObj } = useAuth()

const expenses = ref([])
const filterMonth = ref(new Date().toISOString().slice(0, 7)) // 默认当月 YYYY-MM

const modalVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

// 表单数据
const formData = ref({
  category: '房租 (Alquiler)',
  description: '',
  amount: 0,
  currency: 'USD',
  exchange_rate: 36.50, // 默认值，用户可以改
  payment_method: 'Cash_USD',
  created_by: currentUserObj.value?.username || 'Admin',
  expense_date: new Date().toISOString().split('T')[0]
})

const fetchExpenses = async () => {
  try {
    const url = filterMonth.value ? `/api/expenses?month=${filterMonth.value}` : '/api/expenses'
    const res = await apiFetch(url)
    if (res.ok) {
      expenses.value = await res.json()
    }
  } catch (e) {
    console.error('获取支出列表失败', e)
  }
}

const filteredExpenses = computed(() => {
  // 后端已经做了月份过滤，这里直接返回。如果需要前端双重过滤也可以写在这里。
  return expenses.value
})

const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  formData.value = {
    category: '房租 (Alquiler)',
    description: '',
    amount: 0,
    currency: 'USD',
    exchange_rate: 36.50,
    payment_method: 'Cash_USD',
    created_by: currentUserObj.value?.username || 'Admin',
    expense_date: new Date().toISOString().split('T')[0]
  }
  modalVisible.value = true
}

const openEditModal = (item) => {
  isEditing.value = true
  editingId.value = item.id
  formData.value = { ...item }
  modalVisible.value = true
}

const saveExpense = async () => {
  try {
    const method = isEditing.value ? 'PUT' : 'POST'
    const url = isEditing.value ? `/api/expenses/${editingId.value}` : '/api/expenses'
    
    const res = await apiFetch(url, {
      method,
      body: JSON.stringify(formData.value)
    })

    if (res.ok) {
      modalVisible.value = false
      showSuccessModal('✨ 支出记录保存成功')
      fetchExpenses()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 保存失败: ${err.detail || '未知错误'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 服务器连接错误')
  }
}

const confirmDelete = async (id) => {
  if (!confirm('确定要删除这条开支记录吗？')) return
  try {
    const res = await apiFetch(`/api/expenses/${id}`, { method: 'DELETE' })
    if (res.ok) {
      showSuccessModal('🗑️ 记录已删除')
      fetchExpenses()
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchExpenses()
})
</script>