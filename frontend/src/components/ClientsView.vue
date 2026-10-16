<!-- src/components/ClientsView.vue -->
<template>
  <div class="space-y-6">
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3 w-full md:w-auto">
          <div class="relative w-full md:w-72">
            <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
            <input
              :value="clientSearchQuery"
              @input="$emit('update:clientSearchQuery',$event.target.value)"
              type="text"
              :placeholder="t.clientSearchPlaceholder"
              class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all"
            />
          </div>
        </div>

        <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
          <!-- 🌟 批量删除按钮 -->
          <button 
            v-if="selectedIds.length > 0" 
            @click="batchDeleteModalVisible = true" 
            class="flex items-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
          >
            <span>🗑️ 批量删除 (已选 {{ selectedIds.length }} 项)</span>
          </button>

          <button
            @click="$emit('export-clients')"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md transition-all"
          >
            <FileSpreadsheet :size="16" />
            <span>{{ t.exportClientsBtn }}</span>
          </button>
          <button
            @click="$emit('open-add-client')"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md shadow-blue-500/25 transition-all"
          >
            <Plus :size="16" />
            <span>{{ t.addClientBtn }}</span>
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[750px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <!-- 🌟 全选框 -->
              <th class="py-3.5 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-3.5 px-6">{{ t.clientColName }}</th>
              <th class="py-3.5 px-6">{{ t.clientColType }}</th>
              <th class="py-3.5 px-6">{{ t.clientColPhone }}</th>
              <th class="py-3.5 px-6">{{ t.clientColAddress }}</th>
              <th class="py-3.5 px-6">{{ t.clientColRif }}</th>
              <th class="py-3.5 px-6">{{ t.clientColDebt }}</th>
              <th class="py-3.5 px-6 text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="filteredClients.length === 0">
              <td colspan="8" class="text-center py-12 text-slate-400 text-xs">
                {{ t.noClientsFound }}
              </td>
            </tr>
            <tr v-for="c in filteredClients" :key="c.id" class="hover:bg-slate-50/50 transition-colors">
              <!-- 🌟 单选框 -->
              <td class="py-4 px-4 text-center">
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(c.id)" 
                  @change="toggleSelect(c.id)" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </td>
              <td class="py-4 px-6 font-bold text-slate-900">{{ c.name }}</td>
              <td class="py-4 px-6">
                <span :class="['inline-flex px-2.5 py-1 rounded-md text-xs font-semibold',
                  c.client_type === 'Mayorista' ? 'bg-purple-50 text-purple-600' : (c.client_type === 'Taller' ? 'bg-amber-50 text-amber-600' : 'bg-blue-50 text-blue-600')]">
                  {{ c.client_type }}
                </span>
              </td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ c.phone || '-' }}</td>
              <td class="py-4 px-6 text-slate-600">{{ c.address || '-' }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ c.rif_or_cedula || '-' }}</td>
              <td class="py-4 px-6 font-bold text-rose-600">$ {{ (c.debt || 0).toFixed(2) }}</td>
              <td class="py-4 px-6 text-center space-x-2">
                <button @click="$emit('delete-client', c)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-medium transition-colors cursor-pointer">
                  {{ t.btnDelete }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 🌟 批量删除确认弹窗 -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-900/40"
      title="确认批量删除客户"
      :message="`确定要批量删除选中的 ${selectedIds.length} 个客户档案吗？删除后不可恢复。`"
      cancel-text="取消"
      confirm-text="确认删除"
      @cancel="batchDeleteModalVisible = false"
      @confirm="confirmBatchDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Plus, FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({
  clientsList: Array,
  clientSearchQuery: String
})

const emit = defineEmits(['update:clientSearchQuery', 'open-add-client', 'export-clients', 'delete-client', 'refresh-data'])
const { t } = useI18n()
const { showSuccessModal } = useNotifications()

const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)

const filteredClients = computed(() => {
  return props.clientsList.filter(c => {
    return !props.clientSearchQuery ||
      c.name.toLowerCase().includes(props.clientSearchQuery.toLowerCase()) ||
      (c.rif_or_cedula && c.rif_or_cedula.toLowerCase().includes(props.clientSearchQuery.toLowerCase()))
  })
})

const isAllSelected = computed(() => {
  if (filteredClients.value.length === 0) return false
  return filteredClients.value.every(item => selectedIds.value.includes(item.id))
})

const toggleSelectAll = (e) => {
  if (e.target.checked) {
    selectedIds.value = filteredClients.value.map(i => i.id)
  } else {
    selectedIds.value = []
  }
}

const toggleSelect = (id) => {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  } else {
    selectedIds.value.push(id)
  }
}

const confirmBatchDelete = async () => {
  try {
    for (const id of selectedIds.value) {
      await apiFetch(`/api/clients/${id}`, { method: 'DELETE' })
    }
    batchDeleteModalVisible.value = false
    selectedIds.value = []
    showSuccessModal('🗑️ 批量删除客户成功！')
    emit('refresh-data')
  } catch (e) {
    batchDeleteModalVisible.value = false
    showSuccessModal('❌ 批量删除出现异常')
  }
}
</script>