<!-- src/components/PartsView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">
    
    <!-- ==================== 第一层：页面大标题 ==================== -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span>📦</span> {{ t.inventory.title }}
        </h2>
        <p class="text-xs text-slate-500 mt-1">管理汽车配件的入库、出库、定价及多图档案。</p>
      </div>
    </div>

    <!-- ==================== 第二层：操作工具栏 ==================== -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      
      <!-- 左侧：搜索与筛选 -->
      <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
        <!-- 搜索框 -->
        <div class="relative w-full md:w-64">
          <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
          <input
            :value="searchQuery"
            @input="$emit('update:searchQuery',$event.target.value)"
            type="text"
            :placeholder="t.inventory.searchPlaceholder"
            class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all font-bold"
          />
        </div>

        <!-- 品牌下拉 -->
        <div class="relative">
          <select 
            :value="selectedBrand" 
            @change="$emit('update:selectedBrand',$event.target.value)"
            class="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-4 py-2.5 pr-8 outline-none focus:border-blue-500 focus:bg-white transition-all cursor-pointer appearance-none"
          >
            <option value="ALL">🏷️ {{ tExt.allBrands }}</option>
            <option v-for="b in brandsList.filter(item => item !== 'ALL')" :key="b" :value="b">
              {{ b }}
            </option>
          </select>
          <div class="absolute right-3 top-3.5 pointer-events-none text-slate-400 text-xs">▼</div>
        </div>

        <!-- 分类下拉 -->
        <div class="relative">
          <select 
            v-model="selectedCategory" 
            class="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 rounded-xl px-4 py-2.5 pr-8 outline-none focus:border-blue-500 focus:bg-white transition-all cursor-pointer appearance-none"
          >
            <option value="ALL">📂 {{ tExt.allCategories }}</option>
            <option v-for="cat in categoriesList.filter(item => item !== 'ALL')" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
          <div class="absolute right-3 top-3.5 pointer-events-none text-slate-400 text-xs">▼</div>
        </div>
      </div>

      <!-- 右侧：操作按钮 -->
      <div class="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">

        <button 
          v-if="selectedIds.length > 0" 
          @click="openBatchDeleteModal" 
          class="flex items-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
        >
          <span>🗑️ {{ tExt.batchDelete }} ({{ tExt.batchSelected }} {{ selectedIds.length }})</span>
        </button>

        <button
          @click="$emit('open-add-modal')"
          class="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-blue-500/20 transition-all cursor-pointer"
        >
          <Plus :size="16" />
          <span>{{ t.inventory.addBtn }}</span>
        </button>
      </div>
    </div>

    <!-- ==================== 第三层：数据表格 ==================== -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-4 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-4 px-4">{{ t.inventory.colImage }}</th>
              <th class="py-4 px-4">{{ t.inventory.colOem }}</th>
              <th class="py-4 px-4">{{ t.inventory.colName }}</th>
              <th class="py-4 px-4">📍 {{ t.inventory.colBin }}</th>
              <th class="py-4 px-4">{{ t.inventory.colStock }}</th>
              <th class="py-4 px-4">{{ t.inventory.colPriceUsd }}</th>
              <th class="py-4 px-4 text-amber-600">{{ t.inventory.costPrice }}</th>
              <th class="py-4 px-4 text-emerald-600">{{ t.inventory.profit }}</th>
              <th class="py-4 px-4 text-center">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr 
              v-for="item in paginatedParts" 
              :key="item.id || item.oem" 
              class="hover:bg-blue-50/30 transition-colors cursor-pointer group"
              @click="openDetailDrawer(item)"
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
                    {{ t.inventory.noImage }}
                  </div>
                </div>
              </td>

              <td class="py-4 px-4 font-mono font-bold text-slate-800">{{ item.oem }}</td>
              <td class="py-4 px-4 font-medium text-slate-900">{{ item.name }}</td>

              <!-- 货架库位 -->
              <td class="py-4 px-4">
                <span class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-lg text-xs font-semibold font-mono border border-emerald-200/60">
                  📍 {{ item.bin_location || '—' }}
                </span>
              </td>

              <td class="py-4 px-4 font-bold" :class="item.stock <= 5 ? 'text-rose-600' : 'text-slate-800'">{{ item.stock }}</td>
              
              <td class="py-4 px-4 font-bold text-blue-600">$ {{ Number(item.price || 0).toFixed(2) }}</td>
              
              <td class="py-4 px-4 font-bold text-amber-600">$ {{ Number(item.cost_price || 0).toFixed(2) }}</td>

              <td class="py-4 px-4 font-black">
                <span :class="(item.price - (item.cost_price || 0)) > 0 ? 'text-emerald-600' : 'text-rose-500'">
                  $ {{ Number((item.price || 0) - (item.cost_price || 0)).toFixed(2) }}
                </span>
              </td>

              <!-- 操作列：仅保留删除 -->
              <td class="py-4 px-4 text-center" @click.stop>
                <button @click="$emit('delete-part', item)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1 rounded-lg font-semibold transition-colors cursor-pointer">
                  {{ t.common.delete }}
                </button>
              </td>
            </tr>
            <tr v-if="filteredParts.length === 0">
              <td colspan="10" class="py-16 text-center text-slate-400 text-sm">
                <span class="text-4xl block mb-3">📭</span>
                {{ tExt.emptyParts }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs">
        <span class="text-slate-500 font-medium">
          {{ tExt.showing }} <strong class="text-slate-800">{{ (currentPage - 1) * pageSize + 1 }}</strong> {{ tExt.to }} <strong class="text-slate-800">{{ Math.min(currentPage * pageSize, filteredParts.length) }}</strong> {{ tExt.of }} <strong class="text-slate-800">{{ filteredParts.length }}</strong> {{ tExt.products }}
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">{{ tExt.jumpTo }}</span>
            <input 
              type="number" 
              min="1" 
              :max="totalPages" 
              v-model.number="jumpPageInput" 
              @keyup.enter="handleJumpPage"
              class="w-12 text-center font-mono font-bold text-blue-600 bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-blue-500 text-xs" 
            />
            <span class="text-slate-400 text-[11px]">/ {{ totalPages }} {{ tExt.page }}</span>
            <button 
              @click="handleJumpPage" 
              class="bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]"
            >
              {{ tExt.jumpBtn }}
            </button>
          </div>

          <div class="flex items-center gap-1.5">
            <button 
              @click="currentPage--" 
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer"
            >
              {{ tExt.prevPage }}
            </button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <button 
              @click="currentPage++" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer"
            >
              {{ tExt.nextPage }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 通用右侧 Drawer 详情/编辑 ==================== -->
    <SideDrawer 
      :visible="detailDrawerVisible" 
      :title="drawerMode === 'read' ? t.inventory.detailTitle : tExt.editTitle" 
      :icon="drawerMode === 'read' ? '📋' : '✏️'"
      @close="closeDrawer"
    >
      <template #header-actions>
        <template v-if="drawerMode === 'read'">
          <button @click="switchToEdit" class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
            {{ t.common.edit }}
          </button>
          <button @click="onDeleteFromDrawer" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
            {{ t.common.delete }}
          </button>
        </template>
      </template>

      <div class="p-6">
        <!-- 只读态 -->
        <div v-if="drawerMode === 'read'" class="space-y-5">
          <div v-if="parseImages(editingPart.image_url).length > 0" class="flex flex-wrap gap-2">
            <div 
              v-for="(img, idx) in parseImages(editingPart.image_url)" 
              :key="idx"
              @click="$emit('open-gallery', parseImages(editingPart.image_url), idx)"
              class="w-20 h-20 rounded-xl overflow-hidden border border-slate-200 cursor-pointer hover:scale-105 transition-transform"
            >
              <img :src="img.startsWith('http') ? img : apiUrl(img)" class="w-full h-full object-cover" />
            </div>
          </div>
          <div v-else class="w-full h-24 rounded-xl bg-slate-50 border border-dashed border-slate-200 flex items-center justify-center text-slate-400 text-xs">
            {{ t.inventory.noImage }}
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colOem }}</p>
              <p class="font-mono font-bold text-slate-800">{{ editingPart.oem }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colName }}</p>
              <p class="font-medium text-slate-900">{{ editingPart.name }}</p>
            </div>
            
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colStock }}</p>
              <p class="font-bold font-mono" :class="editingPart.stock <= 5 ? 'text-rose-600' : 'text-slate-800'">{{ editingPart.stock }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colBin }}</p>
              <p class="font-mono text-slate-800">{{ editingPart.bin_location || '—' }}</p>
            </div>
            
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colPriceUsd }}</p>
              <p class="font-bold text-blue-600">$ {{ Number(editingPart.price || 0).toFixed(2) }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.costPrice }}</p>
              <p class="font-bold text-amber-600">$ {{ Number(editingPart.cost_price || 0).toFixed(2) }}</p>
            </div>
            
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.profit }}</p>
              <p class="font-black" :class="(editingPart.price - (editingPart.cost_price || 0)) > 0 ? 'text-emerald-600' : 'text-rose-500'">
                $ {{ Number((editingPart.price || 0) - (editingPart.cost_price || 0)).toFixed(2) }}
              </p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.taxRate }}</p>
              <p class="font-bold text-slate-800">
                {{ editingPart.tax_rate === 0.16 ? t.inventory.tax16 : (editingPart.tax_rate === 0.08 ? t.inventory.tax8 : t.inventory.tax0) }}
              </p>
            </div>
            
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colCategory }}</p>
              <p class="text-slate-700">{{ editingPart.category || tExt.uncategorized }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colBrand }}</p>
              <p class="text-slate-700">{{ editingPart.brand || '—' }}</p>
            </div>
          </div>

          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">🔗 {{ tExt.crossRef }}</p>
            <p class="text-xs font-mono text-slate-600 bg-slate-50 rounded-xl p-3 whitespace-pre-wrap min-h-[48px]">{{ editingPart.cross_references || '—' }}</p>
          </div>
        </div>

        <!-- 编辑态 -->
        <div v-else class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colOem }}</label>
              <input v-model="editingPart.oem" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono font-bold outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colName }}</label>
              <input v-model="editingPart.name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colCategory }}</label>
              <input v-model="editingPart.category" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colBrand }}</label>
              <input v-model="editingPart.brand" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colStock }}</label>
              <input v-model.number="editingPart.stock" type="number" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colPriceUsd }}</label>
              <input v-model.number="editingPart.price" type="number" step="0.5" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-amber-600 mb-1">{{ t.inventory.costPrice }}</label>
              <input v-model.number="editingPart.cost_price" type="number" step="0.5" min="0" class="w-full bg-amber-50 border border-amber-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono text-amber-900 outline-none focus:border-amber-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.taxRate }}</label>
              <select v-model.number="editingPart.tax_rate" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold outline-none focus:border-blue-500 cursor-pointer">
                <option :value="0.16">{{ t.inventory.tax16 }}</option>
                <option :value="0.08">{{ t.inventory.tax8 }}</option>
                <option :value="0.0">{{ t.inventory.tax0 }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colBin }}</label>
              <input v-model="editingPart.bin_location" type="text" :placeholder="t.inventory.binPlaceholder" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono outline-none focus:border-blue-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">🔗 {{ tExt.crossRef }}</label>
            <textarea 
              v-model="editingPart.cross_references" 
              rows="3" 
              placeholder="WIX: 51348 / Donaldson: P550020..." 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs outline-none focus:border-blue-500 font-mono leading-relaxed resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.updateImages }}</label>
            <input type="file" @change="handleEditFileChange" accept="image/*" multiple class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-200 rounded-xl p-1.5" />
          </div>
        </div>
      </div>

      <!-- 底部操作区 -->
      <template #footer>
        <div v-if="drawerMode === 'edit'" class="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button @click="switchToRead" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            {{ t.common.cancel }}
          </button>
          <button @click="saveEditedPart" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer">
            {{ tExt.saveChanges }}
          </button>
        </div>
      </template>
    </SideDrawer>

    <!-- 批量删除确认 -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-900/40"
      :title="tExt.batchDeleteTitle"
      :message="tExt.batchDeleteMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
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
import SideDrawer from './SideDrawer.vue'
const props = defineProps({
  partsList: Array,
  searchQuery: String,
  selectedBrand: String,
  brandsList: Array,
  bcvRate: Number
})

// 🌟 合并所有 emit 事件，加了 download-template
const emit = defineEmits(['open-add-modal', 'open-gallery', 'delete-part', 'refresh-data'])
const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    allBrands: isZh ? '全部品牌' : isEs ? 'Todas las Marcas' : 'All Brands',
    allCategories: isZh ? '全部分类' : isEs ? 'Todas las Categorías' : 'All Categories',
    uncategorized: isZh ? '未分类' : isEs ? 'Sin categoría' : 'Uncategorized',
    batchDelete: isZh ? '批量删除' : isEs ? 'Eliminar Lote' : 'Batch Delete',
    batchSelected: isZh ? '已选' : isEs ? 'seleccionados' : 'selected',
    emptyParts: isZh ? '没有找到符合条件的商品档案' : isEs ? 'No se encontraron repuestos' : 'No parts found',
    showing: isZh ? '显示第' : isEs ? 'Mostrando' : 'Showing',
    to: isZh ? '到' : isEs ? 'a' : 'to',
    of: isZh ? '条，共' : isEs ? 'de' : 'of',
    products: isZh ? '个商品' : isEs ? 'productos' : 'items',
    jumpTo: isZh ? '跳转到' : isEs ? 'Ir a' : 'Go to',
    page: isZh ? '页' : isEs ? 'Página' : 'Page',
    jumpBtn: isZh ? '跳转' : isEs ? 'Ir' : 'Go',
    prevPage: isZh ? '上一页' : isEs ? 'Anterior' : 'Prev',
    nextPage: isZh ? '下一页' : isEs ? 'Siguiente' : 'Next',
    editTitle: isZh ? '编辑配件档案' : isEs ? 'Editar Repuesto' : 'Edit Part',
    crossRef: isZh ? '交叉适配编号与备注' : isEs ? 'Referencias Cruzadas / Notas' : 'Cross-References / Notes',
    updateImages: isZh ? '更新实物多图 (可选)' : isEs ? 'Actualizar fotos (Opcional)' : 'Update photos (Optional)',
    saveChanges: isZh ? '保存修改' : isEs ? 'Guardar Cambios' : 'Save Changes',
    batchDeleteTitle: isZh ? '确认批量删除商品' : isEs ? 'Confirmar Eliminación en Lote' : 'Confirm Batch Delete',
    batchDeleteMsg: isZh ? `确定要批量删除选中的 ${selectedIds.value.length} 个商品档案吗？删除后不可恢复。` : isEs ? `¿Eliminar ${selectedIds.value.length} repuestos seleccionados? No se puede deshacer.` : `Delete ${selectedIds.value.length} selected parts? Cannot be undone.`,
  }
})

const pageSize = 10
const currentPage = ref(1)
const jumpPageInput = ref(1)
const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)

const selectedCategory = ref('ALL')

const categoriesList = computed(() => {
  return [
    'ALL',
    ...Array.from(new Set(props.partsList.map(p => p.category || tExt.value.uncategorized)))
  ]
})

const detailDrawerVisible = ref(false)
const drawerMode = ref('read')

const editingPart = ref({ 
  id: null, oem: '', name: '', brand: '', category: '', stock: 0, 
  price: 0, cost_price: 0, tax_rate: 0.16, bin_location: '', cross_references: '', image_url: ''
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
    const itemCat = i.category || tExt.value.uncategorized
    const matchCategory = selectedCategory.value === 'ALL' || itemCat === selectedCategory.value

    if (!query) return matchBrand && matchCategory

    const cleanOem = i.oem ? i.oem.toLowerCase().replace(/[^a-z0-9]/g, '') : ''
    const cleanName = i.name ? i.name.toLowerCase() : ''
    const cleanBrand = i.brand ? i.brand.toLowerCase() : ''
    const rawOem = i.oem ? i.oem.toLowerCase() : ''
    const rawName = i.name ? i.name.toLowerCase() : ''
    const rawCross = i.cross_references ? i.cross_references.toLowerCase() : ''

    const matchSearch = 
      cleanOem.includes(cleanQuery) || rawOem.includes(query) || 
      cleanName.includes(query) || rawName.includes(query) ||
      cleanBrand.includes(query) || rawCross.includes(query)

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

const handleJumpPage = () => {
  let target = parseInt(jumpPageInput.value)
  if (isNaN(target)) return
  if (target < 1) target = 1
  if (target > totalPages.value) target = totalPages.value
  currentPage.value = target
  jumpPageInput.value = target
}

watch([() => props.searchQuery, () => props.selectedBrand, selectedCategory], () => {
  currentPage.value = 1
  jumpPageInput.value = 1
  selectedIds.value = []
})

watch(currentPage, (val) => {
  jumpPageInput.value = val
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
    showSuccessModal('🗑️ ' + t.value.common.success)
    emit('refresh-data')
  } catch (e) {
    batchDeleteModalVisible.value = false
    showSuccessModal('❌ ' + t.value.common.error)
  }
}

const openDetailDrawer = (item) => {
  editingPart.value = { 
    ...item, 
    cost_price: item.cost_price ?? 0,
    tax_rate: item.tax_rate ?? 0.16,
    bin_location: item.bin_location || '',
    cross_references: item.cross_references || '',
    image_url: item.image_url || ''
  }
  editFiles.value = []
  drawerMode.value = 'read'
  detailDrawerVisible.value = true
}

const switchToEdit = () => {
  drawerMode.value = 'edit'
}

const switchToRead = () => {
  const latest = props.partsList.find(p => p.id === editingPart.value.id)
  if (latest) {
    editingPart.value = {
      ...latest,
      cost_price: latest.cost_price ?? 0,
      tax_rate: latest.tax_rate ?? 0.16,
      bin_location: latest.bin_location || '',
      cross_references: latest.cross_references || '',
      image_url: latest.image_url || ''
    }
  }
  editFiles.value = []
  drawerMode.value = 'read'
}

const closeDrawer = () => {
  detailDrawerVisible.value = false
  editFiles.value = []
  drawerMode.value = 'read'
}

const onDeleteFromDrawer = () => {
  emit('delete-part', editingPart.value)
  closeDrawer()
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
    formData.append('category', editingPart.value.category || tExt.value.uncategorized)
    formData.append('stock', editingPart.value.stock ?? 0)
    formData.append('price', editingPart.value.price ?? 0.0)
    formData.append('cost_price', editingPart.value.cost_price ?? 0.0)
    formData.append('tax_rate', editingPart.value.tax_rate ?? 0.16)
    formData.append('bin_location', editingPart.value.bin_location || '')
    formData.append('cross_references', editingPart.value.cross_references || '')

    editFiles.value.forEach(f => formData.append('files', f))

    const res = await apiFetch(`/api/parts/${editingPart.value.id}`, {
      method: 'PUT',
      body: formData
    })

    if (res.ok) {
      editFiles.value = []
      drawerMode.value = 'read'
      showSuccessModal('✨ ' + t.value.common.success)
      emit('refresh-data')
    } else {
      const err = await res.json()
      showSuccessModal(`❌ ${t.value.common.error}: ${err.detail || 'Unknown'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ ' + t.value.common.error)
  }
}

const handleKeydown = (e) => {
  if (!detailDrawerVisible.value && !batchDeleteModalVisible.value) return
  if (e.key === 'Escape') {
    if (detailDrawerVisible.value) {
      if (drawerMode.value === 'edit') {
        switchToRead()
      } else {
        closeDrawer()
      }
    }
    if (batchDeleteModalVisible.value) {
      batchDeleteModalVisible.value = false
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>