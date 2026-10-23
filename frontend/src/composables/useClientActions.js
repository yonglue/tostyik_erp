import { ref } from 'vue'
import { apiFetch } from '../utils/api'
import { useNotifications } from './useNotifications'
import { useInventory } from './useInventory'
import { useI18n } from './useI18n'

export function useClientActions() {
  const { showSuccessModal } = useNotifications()
  const { fetchClients } = useInventory()
  const { t, currentLang } = useI18n()

  const clientDialogVisible = ref(false)
  const deleteClientModalVisible = ref(false)
  const targetClient = ref(null)
  
  // 核心字段：包含 store_name
  const newClient = ref({ 
    name: '', 
    store_name: '', 
    phone: '', 
    address: '', 
    rif_or_cedula: '', 
    client_type: 'Regular', 
    notes: '' 
  })

  // 🌟 内部工具：直接获取翻译，不需要从外部传 tExt 进来
  const getToastMsg = (key) => {
    const isZh = currentLang.value === 'zh'
    const isEs = currentLang.value === 'es'
    const msgs = {
      toastClientAdded: isZh ? '新客户档案创建成功！' : isEs ? '¡Cliente creado con éxito!' : 'Client created successfully!',
      toastClientDeleted: isZh ? '客户档案已成功删除！' : isEs ? '¡Cliente eliminado con éxito!' : 'Client deleted successfully!',
      toastErrorUnknown: isZh ? '未知错误' : isEs ? 'Error desconocido' : 'Unknown error',
      toastServerError: isZh ? '服务器连接异常！' : isEs ? '¡Error de conexión al servidor!' : 'Server connection error!'
    }
    return msgs[key] || key
  }

  // 🌟 移除了 tExt 参数
  const handleAddClient = async () => {
    if (!newClient.value.name) return
    
    try {
      const res = await apiFetch('/api/clients', {
        method: 'POST',
        body: JSON.stringify(newClient.value)
      })
      
      if (res.ok) {
        clientDialogVisible.value = false
        // 重置表单时包含 store_name
        newClient.value = { name: '', store_name: '', phone: '', address: '', rif_or_cedula: '', client_type: 'Regular', notes: '' }
        fetchClients()
        showSuccessModal('✨ ' + getToastMsg('toastClientAdded'))
      } else {
        const err = await res.json().catch(() => ({}))
        const errorMsg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail || '未知错误')
        showSuccessModal(`❌ 新建客户失败: ${errorMsg}`) 
      }
    } catch (e) {
      console.error(e)
      showSuccessModal('❌ 网络连接异常')
    }
  }

  const openDeleteClientModal = (c) => {
    targetClient.value = c
    deleteClientModalVisible.value = true
  }

  // 🌟 移除了 tExt 参数
  const confirmDeleteClient = async () => {
    if (!targetClient.value) return
    try {
      const res = await apiFetch(`/api/clients/${targetClient.value.id}`, { method: 'DELETE' })
      if (res.ok) {
        deleteClientModalVisible.value = false
        targetClient.value = null
        fetchClients()
        showSuccessModal('🗑️ ' + getToastMsg('toastClientDeleted'))
      } else {
        const err = await res.json()
        deleteClientModalVisible.value = false
        showSuccessModal(`❌ ${t.value.common.error}: ${err.detail || getToastMsg('toastErrorUnknown')}`)
      }
    } catch (e) {
      console.error(e)
      deleteClientModalVisible.value = false
      showSuccessModal('❌ ' + getToastMsg('toastServerError'))
    }
  }

  return {
    clientDialogVisible, deleteClientModalVisible, targetClient, newClient,
    handleAddClient, openDeleteClientModal, confirmDeleteClient
  }
}