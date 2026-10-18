<!-- src/components/PartsView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部统一的操作栏与搜索、下拉筛选 -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
        <!-- 搜索框 -->
        <div class="relative w-full md:w-64">
          <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
          <input
            :value="searchQuery"
            @input="$emit('update:searchQuery',$event.target.value)"
            type="text"
            :placeholder="t.searchPlaceholder || '搜索配件名称或 OEM 编号...'"
            class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all"
          />
        </div>

        <!-- 🌟 品牌下拉选择器 -->
        <div class="relative">
          <select 
            :value="selectedBrand" 
            @change="$emit('update:selectedBrand',$event.target.value)"
            class="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-4 py-2.5 pr-8 outline-none focus:border-blue-500 focus:bg-white transition-all cursor-pointer appearance-none"
          >
            <option value="ALL">🏷️ 全部品牌 (All Brands)</option>
            <option v-for="b in brandsList.filter(item => item !== 'ALL')" :key="b" :value="b">
              {{ b }}
            </option>
          </select>
          <div class="absolute right-3 top-3.5 pointer-events-none text-slate-400 text-xs">▼</div>
        </div>

        <!-- 🌟 配件分类下拉选择器 -->
        <div class="relative">
          <select 
            v-model="selectedCategory" 
            class="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-4 py-2.5 pr-8 outline-none focus:border-blue-500 focus:bg-white transition-all cursor-pointer appearance-none"
          >
            <option value="ALL">📂 全部分类 (All Categories)</option>
            <option v-for="cat in categoriesList.filter(item => item !== 'ALL')" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
          <div class="absolute right-3 top-3.5 pointer-events-none text-slate-400 text-xs">▼</div>
        </div>
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
        <!-- 批量删除按钮 -->
        <button 
          v-if="selectedIds.length > 0" 
          @click="openBatchDeleteModal" 
          class="flex items-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
        >
          <span>🗑️ 批量删除 (已选 {{ selectedIds.length }} 项)</span>
        </button>

        <button
          @click="$emit('open-add-modal')"
          class="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md shadow-blue-500/25 transition-all cursor-pointer"
        >
          <Plus :size="16" />
          <span>{{ t.addPartBtn || '新增配件' }}</span>
        </button>
      </div>
    </div>

    <!-- 🌟 合并后的主商品表格 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[950px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-3.5 px-4">实物多图</th>
              <th class="py-3.5 px-4">{{ t.colOem || 'OEM 编号' }}</th>
              <th class="py-3.5 px-4">{{ t.colName || '配件名称' }}</th>
              <th class="py-3.5 px-4">📍 货架库位</th>
              <th class="py-3.5 px-4">{{ t.colCategory || '分类' }}</th>
              <th class="py-3.5 px-4">{{ t.colBrand || '品牌' }}</th>
              <th class="py-3.5 px-4">税率类型 (IVA)</th>
              <th class="py-3.5 px-4">{{ t.colStock || '库存' }}</th>
              <th class="py-3.5 px-4">{{ t.colPriceUsd || '售价 (USD)' }}</th>
              <th class="py-3.5 px-4 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr 
              v-for="item in paginatedParts" 
              :key="item.id || item.oem" 
              class="hover:bg-blue-50/30 transition-colors cursor-pointer group"
              @click="openEditModal(item)"
            >
              <!-- 多选框 -->
              <td class="py-4 px-4 text-center" @click.stop>
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(item.id)" 
                  @change="toggleSelect(item.id)" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </td>

              <!-- 实物多图 -->
              <td class="py-4 px-4" @click.stop>
                <div class="flex items-center gap-1.5">
                  <template v-if="parseImages(item.image_url).length > 0">
                    <div 
                      @click="$emit('open-gallery', parseImages(item.image_url), 0)"
                      class="w-10 h-10 rounded-xl overflow-hidden border border-slate-200 cursor-pointer hover:scale-105 transition-transform shadow-2xs relative group/img"
                    >
                      <img :src="parseImages(item.image_url)[0].startsWith('http') ? parseImages(item.image_url)[0] : apiUrl(parseImages(item.image_url)[0])" class="w-full h-full object-cover" />
                      <div v-if="parseImages(item.image_url).length > 1" class="absolute bottom-0 right-0 bg-slate-900/70 text-white text-[8px] px-1 rounded-tl font-mono">
                        +{{ parseImages(item.image_url).length - 1 }}
                      </div>
                    </div>
                  </template>
                  <div v-else class="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400 text-[10px] font-bold">
                    No 🖼️
                  </div>
                </div>
              </td>

              <td class="py-4 px-4 font-mono font-bold text-slate-800">{{ item.oem }}</td>
              <td class="py-4 px-4 font-medium text-slate-900">{{ item.name }}</td>

              <!-- 📍 货架库位胶囊 -->
              <td class="py-4 px-4">
                <span class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-lg text-xs font-semibold font-mono border border-emerald-200/60">
                  📍 {{ item.bin_location || 'Estante A-1' }}
                </span>
              </td>

              <td class="py-4 px-4 text-slate-600">
                <span class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded text-xs font-semibold">{{ item.category || '未分类' }}</span>
              </td>
              <td class="py-4 px-4 text-slate-600">
                <span class="bg-slate-100 px-2.5 py-1 rounded-md text-xs font-medium">{{ item.brand }}</span>
              </td>

              <!-- 🌟 新增：显示商品税率类型 -->
              <td class="py-4 px-4">
                <span :class="item.tax_rate > 0 ? 'bg-amber-50 text-amber-700 border-amber-200/60' : 'bg-slate-100 text-slate-600 border-slate-200'" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold border">
                  {{ item.tax_rate > 0 ? '16% IVA' : '0% 免税' }}
                </span>
              </td>

              <td class="py-4 px-4 font-bold" :class="item.stock <= 5 ? 'text-rose-600' : 'text-slate-800'">{{ item.stock }}</td>
              <td class="py-4 px-4 font-bold text-blue-600">$ {{ Number(item.price || 0).toFixed(2) }}</td>

              <td class="py-4 px-4 text-center" @click.stop>
                <div class="inline-flex items-center justify-center gap-2">
                  <button @click="openEditModal(item)" class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1 rounded-lg font-semibold transition-colors cursor-pointer">
                    编辑
                  </button>
                  <button @click="$emit('delete-part', item)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1 rounded-lg font-semibold transition-colors cursor-pointer">
                    删除
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredParts.length === 0">
              <td colspan="11" class="py-12 text-center text-slate-400 text-xs">没有找到符合条件的商品档案</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页栏 -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs">
        <span class="text-slate-500 font-medium">
          显示第 <strong class="text-slate-800">{{ (currentPage - 1) * pageSize + 1 }}</strong> 到 <strong class="text-slate-800">{{ Math.min(currentPage * pageSize, filteredParts.length) }}</strong> 条，共 <strong class="text-slate-800">{{ filteredParts.length }}</strong> 个商品
        </span>
        <div class="flex items-center gap-1.5">
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer"
          >
            上一页
          </button>
          <span class="px-3 py-1 font-mono font-bold text-slate-700">
            {{ currentPage }} / {{ totalPages }}
          </span>
          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages"
            class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 🌟 编辑配件档案弹窗 -->
    <div 
      v-if="editModalVisible" 
      @click.self="editModalVisible = false" 
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 transition-all"
    >
      <div class="bg-white rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">✏️</span>
            <h3 class="font-bold text-slate-800 text-base">编辑配件档案 (SKU #{{ editingPart.id }})</h3>
          </div>
          <button @click="editModalVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer">✕</button>
        </div>

        <form @submit.prevent="saveEditedPart" class="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">OEM 编号</label>
              <input v-model="editingPart.oem" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono font-bold outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">配件名称</label>
              <input v-model="editingPart.name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">配件分类</label>
              <input v-model="editingPart.category" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">适配品牌</label>
              <input v-model="editingPart.brand" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">库存数量</label>
              <input v-model.number="editingPart.stock" type="number" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">零售价格 (USD)</label>
              <input v-model.number="editingPart.price" type="number" step="0.5" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">商品税率属性 (IVA)</label>
              <select v-model.number="editingPart.tax_rate" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold outline-none focus:border-blue-500 cursor-pointer">
                <option :value="0.16">16% 标准增值税 (IVA)</option>
                <option :value="0.0">0% 免税 (Exento)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">货架库位 (Bin Location)</label>
              <input v-model="editingPart.bin_location" type="text" placeholder="Estante A-1" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono outline-none focus:border-blue-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">
              🔗 交叉适配编号与备注 (Cross-References / Notes)
            </label>
            <textarea 
              v-model="editingPart.cross_references" 
              rows="3" 
              placeholder="例如: WIX: 51348 / Donaldson: P550020..." 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs outline-none focus:border-blue-500 font-mono leading-relaxed resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">更新实物多图 (可选)</label>
            <input type="file" @change="handleEditFileChange" accept="image/*" multiple class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-200 rounded-xl p-1.5" />
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="editModalVisible = false" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
              取消 (ESC)
            </button>
            <button type="submit" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer">
              保存修改 (Enter)
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 🌟 现代化风格的批量删除确认弹窗 -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-900/40"
      title="确认批量删除商品"
      :message="`确定要批量删除选中的 ${selectedIds.length} 个商品档案吗？删除后不可恢复。`"
      cancel-text="取消"
      confirm-text="确认删除"
      @cancel="batchDeleteModalVisible = false"
      @confirm="confirmBatchDelete"
    />

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Search, Plus } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiUrl, apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({
  partsList: Array,
  searchQuery: String,
  selectedBrand: String,
  brandsList: Array,
  bcvRate: Number
})

const emit = defineEmits(['update:searchQuery', 'update:selectedBrand', 'open-add-modal', 'open-gallery', 'delete-part', 'refresh-data'])
const { t } = useI18n()
const { showSuccessModal } = useNotifications()

const pageSize = 8
const currentPage = ref(1)
const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)

const selectedCategory = ref('ALL')

const categoriesList = computed(() => {
  return [
    'ALL',
    ...Array.from(new Set(props.partsList.map(p => p.category || '未分类')))
  ]
})

const editModalVisible = ref(false)
const editingPart = ref({ 
  id: null, 
  oem: '', 
  name: '', 
  brand: '', 
  category: '', 
  stock: 0, 
  price: 0, 
  tax_rate: 0.16,
  bin_location: 'Estante A-1',
  cross_references: '' 
})
const editFiles = ref([])

const parseImages = (imageUrlStr) => {
  if (!imageUrlStr) return []
  try {
    const parsed = JSON.parse(imageUrlStr)
    if (Array.isArray(parsed)) return parsed.slice(0, 5)
  } catch (e) {
    if (imageUrlStr.startsWith('http') || imageUrlStr.startsWith('/uploads/')) return [imageUrlStr]
  }
  return []
}

const filteredParts = computed(() => {
  const query = props.searchQuery ? props.searchQuery.trim().toLowerCase() : ''
  const cleanQuery = query.replace(/[^a-z0-9]/g, '')

  return props.partsList.filter(i => {
    const matchBrand = props.selectedBrand === 'ALL' || i.brand === props.selectedBrand
    const itemCat = i.category || '未分类'
    const matchCategory = selectedCategory.value === 'ALL' || itemCat === selectedCategory.value

    if (!query) return matchBrand && matchCategory

    const cleanOem = i.oem ? i.oem.toLowerCase().replace(/[^a-z0-9]/g, '') : ''
    const cleanName = i.name ? i.name.toLowerCase() : ''
    const cleanBrand = i.brand ? i.brand.toLowerCase() : ''
    const rawOem = i.oem ? i.oem.toLowerCase() : ''
    const rawName = i.name ? i.name.toLowerCase() : ''
    const rawCross = i.cross_references ? i.cross_references.toLowerCase() : ''

    const matchSearch = 
      cleanOem.includes(cleanQuery) || 
      rawOem.includes(query) || 
      cleanName.includes(query) ||
      rawName.includes(query) ||
      cleanBrand.includes(query) ||
      rawCross.includes(query)

    return matchBrand && matchCategory && matchSearch
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredParts.value.length / pageSize) || 1
})

const paginatedParts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredParts.value.slice(start, start + pageSize)
})

watch([() => props.searchQuery, () => props.selectedBrand, selectedCategory], () => {
  currentPage.value = 1
  selectedIds.value = []
})

const isAllSelected = computed(() => {
  if (paginatedParts.value.length === 0) return false
  return paginatedParts.value.every(item => selectedIds.value.includes(item.id))
})

const toggleSelectAll = (e) => {
  if (e.target.checked) {
    const currentIds = paginatedParts.value.map(i => i.id)
    selectedIds.value = Array.from(new Set([...selectedIds.value, ...currentIds]))
  } else {
    const currentIds = paginatedParts.value.map(i => i.id)
    selectedIds.value = selectedIds.value.filter(id => !currentIds.includes(id))
  }
}

const toggleSelect = (id) => {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  } else {
    selectedIds.value.push(id)
  }
}

const openBatchDeleteModal = () => {
  if (selectedIds.value.length === 0) return
  batchDeleteModalVisible.value = true
}

const confirmBatchDelete = async () => {
  try {
    for (const id of selectedIds.value) {
      await apiFetch(`/api/parts/${id}`, { method: 'DELETE' })
    }
    batchDeleteModalVisible.value = false
    selectedIds.value = []
    showSuccessModal('🗑️ 批量删除成功！')
    emit('refresh-data')
  } catch (e) {
    batchDeleteModalVisible.value = false
    showSuccessModal('❌ 批量删除出现异常')
  }
}

const openEditModal = (item) => {
  editingPart.value = { 
    ...item, 
    tax_rate: item.tax_rate ?? 0.16,
    bin_location: item.bin_location || 'Estante A-1',
    cross_references: item.cross_references || ''
  }
  editFiles.value = []
  editModalVisible.value = true
}

const handleEditFileChange = (e) => {
  editFiles.value = Array.from(e.target.files).slice(0, 5)
}

const saveEditedPart = async () => {
  try {
    const formData = new FormData()
    formData.append('oem', editingPart.value.oem)
    formData.append('name', editingPart.value.name)
    formData.append('brand', editingPart.value.brand || 'GENERAL')
    formData.append('category', editingPart.value.category || '未分类')
    formData.append('stock', editingPart.value.stock ?? 0)
    formData.append('price', editingPart.value.price ?? 0.0)
    formData.append('tax_rate', editingPart.value.tax_rate ?? 0.16)
    formData.append('bin_location', editingPart.value.bin_location || 'Estante A-1')
    formData.append('cross_references', editingPart.value.cross_references || '')

    editFiles.value.forEach(f => formData.append('files', f))

    const res = await apiFetch(`/api/parts/${editingPart.value.id}`, {
      method: 'PUT',
      body: formData
    })

    if (res.ok) {
      editModalVisible.value = false
      showSuccessModal('✨ 商品档案更新成功！')
      emit('refresh-data')
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 更新失败: ${err.detail || '未知错误'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 服务器连接异常！')
  }
}

const handleKeydown = (e) => {
  if (!editModalVisible.value && !batchDeleteModalVisible.value) return
  if (e.key === 'Escape') {
    editModalVisible.value = false
    batchDeleteModalVisible.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>