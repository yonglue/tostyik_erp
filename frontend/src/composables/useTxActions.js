
import { ref } from 'vue'
import { apiFetch } from '../utils/api'
import { useNotifications } from './useNotifications'
import { useI18n } from './useI18n'
import { useInventory } from './useInventory'
import { usePosCart } from './usePosCart'

export function useTxActions({ activeTab }) {
  // 依赖其他 composable
  const { showSuccessModal } = useNotifications()
  const { t, currentLang } = useI18n()
  const { fetchTransactions, fetchParts, fetchDashboardStats } = useInventory()
  const { cartItems, quoteClientName } = usePosCart()

  // 把 tExt 抽出为局部计算属性（只保留与 Tx 相关的）
  // 注意：App.vue 里原来有个庞大的 tExt，这里为了局部化，提取需要的部分
  // 如果 tExt 后续还有别的组件用到，可以留着，这里我们先简单复用 App.vue 的
  // 为避免重复，我们通过 t 直接翻译，或硬编码（这里用原先的逻辑简化）
  
  // --- 状态 ---
  const txDialogVisible = ref(false)
  const isSubmittingTx = ref(false)
  const deleteTxModalVisible = ref(false)
  const targetTxForDelete = ref(null)
  
  const newTx = ref({
    type: 'OUT', // IN 或 OUT
    part_oem: '',
    part_name: '',
    quantity: 1,
    unit_price: 0,
    customer_or_supplier: ''
  })

  // --- 动作 ---
  const handleAddTx = async () => {
    isSubmittingTx.value = true
    try {
      const res = await apiFetch('/api/transactions', {
        method: 'POST',
        body: JSON.stringify(newTx.value)
      })
      if (res.ok) {
        txDialogVisible.value = false
        // 这里的 toast 走原来的 tExt 提示
        const isZh = currentLang.value === 'zh'
        const isEs = currentLang.value === 'es'
        const toastTxAdded = isZh ? '单据录入成功' : isEs ? 'Registro guardado' : 'Record saved'
        showSuccessModal('✨ ' + toastTxAdded)
        
        newTx.value = { type: 'OUT', part_oem: '', part_name: '', quantity: 1, unit_price: 0, customer_or_supplier: '' }
        fetchTransactions()
        fetchParts()
        fetchDashboardStats()
      } else {
        const err = await res.json()
        showSuccessModal(`❌ ${t.value.common.error}: ${err.detail || 'Unknown'}`)
      }
    } catch (e) {
      console.error(e)
      const isZh = currentLang.value === 'zh'
      const isEs = currentLang.value === 'es'
      const toastServerError = isZh ? '服务器连接异常！' : isEs ? '¡Error de conexión al servidor!' : 'Server connection error!'
      showSuccessModal('❌ ' + toastServerError)
    } finally {
      isSubmittingTx.value = false
    }
  }

  const openDeleteTxModal = (tx) => {
    targetTxForDelete.value = tx
    deleteTxModalVisible.value = true
  }

  const confirmDeleteTx = async () => {
    if (!targetTxForDelete.value) return
    try {
      const res = await apiFetch(`/api/transactions/${targetTxForDelete.value.id}`, { method: 'DELETE' })
      if (res.ok) {
        deleteTxModalVisible.value = false
        targetTxForDelete.value = null
        fetchTransactions()
        fetchParts()
        fetchDashboardStats()
      }
    } catch (e) { 
      console.error(e) 
    }
  }

  const handleConvertToPos = (data) => {
    if (data.id) {
      localStorage.setItem('pending_quotation_id', String(data.id))
    }
    // 1. 清空当前购物车
    cartItems.value = []
    
    // 2. 将报价单的明细映射到购物车格式
    data.items.forEach(item => {
      cartItems.value.push({
        oem: item.oem,
        name: item.name,
        brand: item.brand || 'GENERAL',
        price: Number(item.price),
        quantity: Number(item.quantity),
        tax_rate: item.tax_rate ?? 0.16
      })
    })

    // 3. 带上客户名字
    if (data.client_name && data.client_name !== 'Cliente General') {
      quoteClientName.value = data.client_name
    }

    // 4. 跳转到 POS 页面
    activeTab.value = 'desk'
  }

  return {
    txDialogVisible,
    isSubmittingTx,
    newTx,
    deleteTxModalVisible,
    targetTxForDelete,
    handleAddTx,
    openDeleteTxModal,
    confirmDeleteTx,
    handleConvertToPos
  }
}
