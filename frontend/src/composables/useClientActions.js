
import { ref } from 'vue'
import { apiFetch } from '../utils/api'
import { useNotifications } from './useNotifications'
import { useInventory } from './useInventory'
import { useI18n } from './useI18n'

export function useClientActions() {
  const { showSuccessModal } = useNotifications()
  const { fetchClients } = useInventory()
  const { t } = useI18n()

  const clientDialogVisible = ref(false)
  const deleteClientModalVisible = ref(false)
  const targetClient = ref(null)
  
  const newClient = ref({ 
    name: '', phone: '', address: '', 
    rif_or_cedula: '', client_type: 'Regular', notes: '' 
  })

  const handleAddClient = async (tExt) => {
    if (!newClient.value.name) return
    const res = await apiFetch('/api/clients', {
      method: 'POST',
      body: JSON.stringify(newClient.value)
    })
    if (res.ok) {
      clientDialogVisible.value = false
      newClient.value = { name: '', phone: '', address: '', rif_or_cedula: '', client_type: 'Regular', notes: '' }
      fetchClients()
      showSuccessModal('✨ ' + tExt.value.toastClientAdded)
    }
  }

  const openDeleteClientModal = (c) => {
    targetClient.value = c
    deleteClientModalVisible.value = true
  }

  const confirmDeleteClient = async (tExt) => {
    if (!targetClient.value) return
    try {
      const res = await apiFetch(`/api/clients/${targetClient.value.id}`, { method: 'DELETE' })
      if (res.ok) {
        deleteClientModalVisible.value = false
        targetClient.value = null
        fetchClients()
        showSuccessModal('🗑️ ' + tExt.value.toastClientDeleted)
      } else {
        const err = await res.json()
        deleteClientModalVisible.value = false
        showSuccessModal(`❌ ${t.value.common.error}: ${err.detail || tExt.value.toastErrorUnknown}`)
      }
    } catch (e) {
      console.error(e)
      deleteClientModalVisible.value = false
      showSuccessModal('❌ ' + tExt.value.toastServerError)
    }
  }

  return {
    clientDialogVisible, deleteClientModalVisible, targetClient, newClient,
    handleAddClient, openDeleteClientModal, confirmDeleteClient
  }
}
