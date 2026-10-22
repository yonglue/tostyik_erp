<!-- src/components/GastosView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">
    
    <!-- ==================== 第一层：页面大标题 ==================== -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span>💸</span> {{ tExt.title }}
        </h2>
        <p class="text-xs text-slate-500 mt-1">{{ tExt.subtitle }}</p>
      </div>
    </div>

    <!-- ==================== 第二层：操作工具栏 ==================== -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      
      <!-- 左侧：筛选 -->
      <div class="flex items-center gap-3">
        <input 
          type="month" 
          v-model="filterMonth" 
          class="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-4 py-2.5 outline-none focus:border-blue-500 transition-all cursor-pointer"
        />
      </div>

      <!-- 右侧：操作按钮 -->
      <div class="flex items-center gap-3">
        <button @click="fetchExpenses" class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all cursor-pointer">
          🔄 {{ t.common.refresh }}
        </button>
        <button @click="openDetailDrawer(null)" class="flex items-center justify-center gap-2 bg-rose-600 hover:bg-rose-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-rose-500/20 transition-all cursor-pointer">
          ➕ {{ tExt.addBtn }}
        </button>
      </div>
    </div>

    <!-- ==================== 第三层：数据表格 ==================== -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-4 px-6">{{ tExt.colDate }}</th>
              <th class="py-4 px-6">{{ tExt.colCategory }}</th>
              <th class="py-4 px-6">{{ tExt.colDesc }}</th>
              <th class="py-4 px-6">{{ tExt.colAmount }}</th>
              <th class="py-4 px-6">{{ tExt.colAmountUsd }}</th>
              <th class="py-4 px-6">{{ tExt.colMethod }}</th>
              <th class="py-4 px-6">{{ tExt.colUser }}</th>
              <th class="py-4 px-6 text-center">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr 
              v-for="item in filteredExpenses" 
              :key="item.id" 
              class="hover:bg-blue-50/30 transition-colors cursor-pointer group"
              @click="openDetailDrawer(item)"
            >
              <td class="py-4 px-6 font-mono font-bold text-slate-700">{{ item.expense_date }}</td>
              <td class="py-4 px-6">
                <span class="bg-rose-50 text-rose-700 border border-rose-200/60 px-2.5 py-1 rounded-lg text-xs font-bold">
                  {{ getCategoryLabel(item.category) }}
                </span>
              </td>
              <td class="py-4 px-6 font-medium text-slate-900">{{ item.description || '-' }}</td>
              <td class="py-4 px-6 font-mono font-black" :class="item.currency === 'USD' ? 'text-emerald-600' : 'text-blue-600'">
                {{ item.currency === 'USD' ? '$' : 'Bs.' }} {{ Number(item.amount).toFixed(2) }}
              </td>
              <td class="py-4 px-6 font-mono font-bold text-slate-500">
                $ {{ (item.currency === 'USD' ? item.amount : item.amount / item.exchange_rate).toFixed(2) }}
              </td>
              <td class="py-4 px-6 text-xs font-semibold text-slate-500">
                {{ getPaymentMethodLabel(item.payment_method) }}
              </td>
              <td class="py-4 px-6 text-xs text-slate-500">
                {{ item.created_by }}
              </td>
              <td class="py-4 px-6 text-center" @click.stop>
                <button @click="confirmDelete(item.id)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
                  {{ t.common.delete }}
                </button>
              </td>
            </tr>
            <tr v-if="filteredExpenses.length === 0">
              <td colspan="8" class="py-16 text-center text-slate-400 text-sm">
                <span class="text-4xl block mb-3">📭</span>
                {{ tExt.empty }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 通用右侧 Drawer (保持原样) -->
    <SideDrawer 
      :visible="detailDrawerVisible" 
      :title="drawerMode === 'read' ? tExt.detailTitle : (currentExpense?.id ? tExt.editTitle : tExt.addTitle)" 
      :icon="drawerMode === 'read' ? '💸' : '📝'"
      @close="closeDrawer"
    >
      <template #header-actions>
        <template v-if="drawerMode === 'read' && currentExpense?.id">
          <button @click="switchToEdit" class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
            {{ t.common.edit }}
          </button>
        </template>
      </template>

      <div class="p-6">
        <!-- 只读态 -->
        <div v-if="drawerMode === 'read'" class="space-y-5">
          <div class="bg-rose-50/50 p-4 rounded-xl border border-rose-100 space-y-1 text-center">
            <div class="text-xs text-rose-500 font-semibold">{{ tExt.colAmount }}</div>
            <div class="font-black text-rose-600 text-2xl font-mono">
              {{ currentExpense?.currency === 'USD' ? '$' : 'Bs.' }} {{ Number(currentExpense?.amount || 0).toFixed(2) }}
            </div>
            <div class="text-xs text-slate-500 font-mono mt-1">
              ≈ ${{ (currentExpense?.currency === 'USD' ? currentExpense?.amount : currentExpense?.amount / currentExpense?.exchange_rate || 0).toFixed(2) }}
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colDate }}</p>
              <p class="font-mono font-bold text-slate-800">{{ currentExpense?.expense_date }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colCategory }}</p>
              <p class="font-bold text-slate-800">{{ getCategoryLabel(currentExpense?.category) }}</p>
            </div>
            <div class="col-span-2">
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colDesc }}</p>
              <p class="text-slate-700">{{ currentExpense?.description || '-' }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colMethod }}</p>
              <p class="text-slate-700">{{ getPaymentMethodLabel(currentExpense?.payment_method) }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colUser }}</p>
              <p class="text-slate-700">{{ currentExpense?.created_by }}</p>
            </div>
          </div>
        </div>

        <!-- 编辑/新增态 -->
        <div v-else class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colCategory }}</label>
              <select v-model="formData.category" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500 cursor-pointer">
                <option value="Alquiler">{{ tExt.catRent }}</option>
                <option value="Nomina">{{ tExt.catSalary }}</option>
                <option value="Servicios">{{ tExt.catUtilities }}</option>
                <option value="Flete">{{ tExt.catLogistics }}</option>
                <option value="Varios">{{ tExt.catMisc }}</option>
                <option value="Impuestos">{{ tExt.catTaxes }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colDate }}</label>
              <input v-model="formData.expense_date" type="date" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colDesc }}</label>
            <input v-model="formData.description" type="text" :placeholder="tExt.phDesc" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colAmount }}</label>
              <input v-model.number="formData.amount" type="number" step="0.01" min="0" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-mono font-bold outline-none focus:border-rose-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.currency }}</label>
              <select v-model="formData.currency" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500 cursor-pointer">
                <option value="USD">{{ tExt.curUsd }}</option>
                <option value="BS">{{ tExt.curBs }}</option>
              </select>
            </div>
          </div>

          <div v-if="formData.currency === 'BS'" class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.exchangeRate }}</label>
              <input v-model.number="formData.exchange_rate" type="number" step="0.01" min="0" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-mono font-bold outline-none focus:border-rose-500" />
            </div>
            <div class="flex items-end pb-3">
              <span class="text-xs text-slate-500 font-bold">≈ ${{ (formData.amount / formData.exchange_rate || 0).toFixed(2) }}</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colMethod }}</label>
              <select v-model="formData.payment_method" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500 cursor-pointer">
                <option value="Cash_USD">{{ tExt.pmCashUsd }}</option>
                <option value="Cash_BS">{{ tExt.pmCashBs }}</option>
                <option value="Pago_Movil">{{ tExt.pmPagoMovil }}</option>
                <option value="Card_POS">{{ tExt.pmCardPos }}</option>
                <option value="Bank_Transfer">{{ tExt.pmTransfer }}</option>
                <option value="Zelle">Zelle</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colUser }}</label>
              <input v-model="formData.created_by" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-rose-500" />
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作区 -->
      <template #footer>
        <div v-if="drawerMode !== 'read'" class="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button @click="switchToRead" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            {{ t.common.cancel }}
          </button>
          <button @click="saveExpense" :disabled="isSubmitting" class="px-6 py-2.5 bg-rose-600 hover:bg-rose-700 disabled:bg-rose-300 text-white rounded-xl text-xs font-bold shadow-md transition-all cursor-pointer">
            {{ isSubmitting ? '...' : t.common.save }}
          </button>
        </div>
      </template>
    </SideDrawer>

    <!-- 删除确认 -->
    <ConfirmDialog
      :visible="isDeleteVisible"
      overlay-class="bg-slate-950/60"
      :title="tExt.deleteTitle"
      :message="tExt.deleteMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="isDeleteVisible = false"
      @confirm="executeDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import { useAuth } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'
import ConfirmDialog from './ConfirmDialog.vue'
import SideDrawer from './SideDrawer.vue'

const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const { currentUserObj } = useAuth()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '日常开支管理' : isEs ? 'Gestión de Gastos' : 'Expense Management',
    subtitle: isZh ? '记录店铺租金、工资、水电等日常支出，支撑净利润核算。' : isEs ? 'Registre alquiler, salarios, servicios para calcular la ganancia neta.' : 'Record rent, payroll, utilities for net profit calculation.',
    addBtn: isZh ? '记一笔支出' : isEs ? 'Registrar Gasto' : 'Record Expense',
    colDate: isZh ? '支出日期' : isEs ? 'Fecha' : 'Date',
    colCategory: isZh ? '分类' : isEs ? 'Categoría' : 'Category',
    colDesc: isZh ? '详细说明' : isEs ? 'Descripción' : 'Description',
    colAmount: isZh ? '金额' : isEs ? 'Monto' : 'Amount',
    colAmountUsd: isZh ? '折合 USD' : isEs ? 'Equiv. USD' : 'USD Equivalent',
    colMethod: isZh ? '支付方式' : isEs ? 'Método de Pago' : 'Payment Method',
    colUser: isZh ? '经办人' : isEs ? 'Registrado por' : 'Recorded By',
    empty: isZh ? '暂无符合条件的支出记录' : isEs ? 'No hay gastos registrados en este período' : 'No expenses found',
    detailTitle: isZh ? '支出详情' : isEs ? 'Detalle de Gasto' : 'Expense Details',
    addTitle: isZh ? '新增日常开支' : isEs ? 'Nuevo Gasto' : 'New Expense',
    editTitle: isZh ? '编辑支出记录' : isEs ? 'Editar Gasto' : 'Edit Expense',
    phDesc: isZh ? '例如：10月份店铺租金' : isEs ? 'Ej: Alquiler de octubre' : 'E.g. October rent',
    currency: isZh ? '币种' : isEs ? 'Moneda' : 'Currency',
    curUsd: isZh ? '美元 (USD)' : isEs ? 'Dólar (USD)' : 'USD',
    curBs: isZh ? '玻利瓦尔 (Bs.)' : isEs ? 'Bolívar (Bs.)' : 'Bolívar (Bs.)',
    exchangeRate: isZh ? '当前汇率 (Bs/USD)' : isEs ? 'Tasa de Cambio' : 'Exchange Rate',
    catRent: isZh ? '房租 (Alquiler)' : isEs ? 'Alquiler' : 'Rent',
    catSalary: isZh ? '员工工资 (Nómina)' : isEs ? 'Nómina' : 'Payroll',
    catUtilities: isZh ? '水电费 (Servicios)' : isEs ? 'Servicios' : 'Utilities',
    catLogistics: isZh ? '运输/物流 (Flete)' : isEs ? 'Flete / Logística' : 'Freight / Logistics',
    catMisc: isZh ? '办公/杂费 (Varios)' : isEs ? 'Varios' : 'Miscellaneous',
    catTaxes: isZh ? '税费 (Impuestos)' : isEs ? 'Impuestos' : 'Taxes',
    pmCashUsd: isZh ? '现金 (美元)' : isEs ? 'Efectivo USD' : 'Cash USD',
    pmCashBs: isZh ? '现金 (Bs.)' : isEs ? 'Efectivo Bs.' : 'Cash Bs.',
    pmPagoMovil: isZh ? 'Pago Móvil' : isEs ? 'Pago Móvil' : 'Pago Móvil',
    pmCardPos: isZh ? '刷卡 (POS)' : isEs ? 'Punto de Venta' : 'Card POS',
    pmTransfer: isZh ? '银行转账' : isEs ? 'Transferencia' : 'Bank Transfer',
    deleteTitle: isZh ? '删除支出记录' : isEs ? 'Eliminar Gasto' : 'Delete Expense',
    deleteMsg: isZh ? '确定要删除这条开支记录吗？删除后不可恢复。' : isEs ? '¿Está seguro de eliminar este gasto?' : 'Delete this expense? Cannot be undone.',
    toastSaved: isZh ? '支出记录保存成功' : isEs ? 'Gasto guardado con éxito' : 'Expense saved',
    toastDeleted: isZh ? '记录已删除' : isEs ? 'Registro eliminado' : 'Record deleted',
    toastInvalid: isZh ? '请输入有效的金额' : isEs ? 'Ingrese un monto válido' : 'Please enter a valid amount'
  }
})

const expenses = ref([])
const filterMonth = ref(new Date().toISOString().slice(0, 7))

const detailDrawerVisible = ref(false)
const drawerMode = ref('read')
const currentExpense = ref(null)
const isSubmitting = ref(false)

const isDeleteVisible = ref(false)
const deleteTargetId = ref(null)

const formData = ref({})

const getCategoryLabel = (cat) => {
  const map = {
    'Alquiler': tExt.value.catRent,
    'Nomina': tExt.value.catSalary,
    'Servicios': tExt.value.catUtilities,
    'Flete': tExt.value.catLogistics,
    'Varios': tExt.value.catMisc,
    'Impuestos': tExt.value.catTaxes,
    '房租 (Alquiler)': tExt.value.catRent,
    '员工工资 (Nómina)': tExt.value.catSalary,
    '水电费 (Servicios)': tExt.value.catUtilities,
    '运输/物流 (Flete)': tExt.value.catLogistics,
    '办公/杂费 (Varios)': tExt.value.catMisc,
    '税费 (Impuestos)': tExt.value.catTaxes
  }
  return map[cat] || cat
}

const getPaymentMethodLabel = (pm) => {
  const map = {
    'Cash_USD': tExt.value.pmCashUsd,
    'Cash_BS': tExt.value.pmCashBs,
    'Pago_Movil': tExt.value.pmPagoMovil,
    'Card_POS': tExt.value.pmCardPos,
    'Bank_Transfer': tExt.value.pmTransfer,
    'Zelle': 'Zelle'
  }
  return map[pm] || pm
}

const fetchExpenses = async () => {
  try {
    const url = filterMonth.value ? `/api/expenses?month=${filterMonth.value}` : '/api/expenses'
    const res = await apiFetch(url)
    if (res.ok) expenses.value = await res.json()
  } catch (e) { console.error(e) }
}

const filteredExpenses = computed(() => expenses.value)

const openDetailDrawer = (item) => {
  if (item) {
    currentExpense.value = { ...item }
    drawerMode.value = 'read'
  } else {
    currentExpense.value = {}
    formData.value = {
      category: 'Alquiler',
      description: '',
      amount: 0,
      currency: 'USD',
      exchange_rate: 36.50,
      payment_method: 'Cash_USD',
      created_by: currentUserObj.value?.username || 'Admin',
      expense_date: new Date().toISOString().split('T')[0]
    }
    drawerMode.value = 'edit'
  }
  detailDrawerVisible.value = true
}

const switchToEdit = () => { formData.value = { ...currentExpense.value }; drawerMode.value = 'edit' }
const switchToRead = () => { drawerMode.value = 'read' }
const closeDrawer = () => { detailDrawerVisible.value = false; drawerMode.value = 'read' }

const saveExpense = async () => {
  if (formData.value.amount <= 0) return showSuccessModal('❌ ' + tExt.value.toastInvalid)
  isSubmitting.value = true
  const isEdit = !!currentExpense.value?.id
  try {
    const res = await apiFetch(isEdit ? `/api/expenses/${currentExpense.value.id}` : '/api/expenses', {
      method: isEdit ? 'PUT' : 'POST',
      body: JSON.stringify(formData.value)
    })
    if (res.ok) {
      showSuccessModal('✨ ' + tExt.value.toastSaved)
      const savedData = await res.json()
      currentExpense.value = isEdit ? { ...currentExpense.value, ...formData.value } : savedData
      drawerMode.value = 'read'
      fetchExpenses()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ ${err.detail || 'Error'}`)
    }
  } catch (e) { console.error(e) } finally { isSubmitting.value = false }
}

const confirmDelete = (id) => {
  deleteTargetId.value = id
  isDeleteVisible.value = true
}

const executeDelete = async () => {
  if (!deleteTargetId.value) return
  try {
    const res = await apiFetch(`/api/expenses/${deleteTargetId.value}`, { method: 'DELETE' })
    if (res.ok) {
      showSuccessModal('🗑️ ' + tExt.value.toastDeleted)
      fetchExpenses()
      if (currentExpense.value?.id === deleteTargetId.value) closeDrawer()
    }
  } catch (e) { console.error(e) } finally {
    isDeleteVisible.value = false
    deleteTargetId.value = null
  }
}

onMounted(() => { fetchExpenses() })
</script>