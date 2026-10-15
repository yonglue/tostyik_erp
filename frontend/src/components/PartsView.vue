<!-- src/components/PartsView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部 Tab 页签切换栏 -->
    <div class="flex items-center justify-between bg-white px-6 py-3 rounded-2xl border border-slate-200/80 shadow-xs">
      <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
        <button 
          @click="activeSubTab = 'stock'"
          :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', 
            activeSubTab === 'stock' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
        >
          📦 商品库存明细
        </button>
        <button 
          @click="activeSubTab = 'warehouse'"
          :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', 
            activeSubTab === 'warehouse' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
        >
          🏢 仓库货架与库位对照 (Bin Location)
        </button>
      </div>

      <!-- 快捷状态提示 -->
      <div class="text-xs font-mono text-slate-400 hidden sm:block">
        SKU 总数: <span class="font-bold text-slate-700">{{ partsList.length }}</span>
      </div>
    </div>

    <!-- 🌟 子视图 1：商品库存明细表格 -->
    <div v-if="activeSubTab === 'stock'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
          <div class="relative w-full md:w-72">
            <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
            <input
              :value="searchQuery"
              @input="$emit('update:searchQuery', $event.target.value)"
              type="text"
              :placeholder="t.searchPlaceholder"
              class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all"
            />
          </div>
          <div class="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl overflow-x-auto max-w-full">
            <button 
              v-for="b in brandsList" 
              :key="b" 
              @click="$emit('update:selectedBrand', b)"
              :class="['px-3 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer', selectedBrand === b ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
            >
              {{ b === 'ALL' ? t.allBrands : b }}
            </button>
          </div>
        </div>

        <button
          @click="$emit('open-add-modal')"
          class="w-full md:w-auto flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md shadow-blue-500/25 transition-all cursor-pointer"
        >
          <Plus :size="16" />
          <span>{{ t.addPartBtn }}</span>
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-6">实物多图</th>
              <th class="py-3.5 px-6">{{ t.colOem }}</th>
              <th class="py-3.5 px-6">{{ t.colName }}</th>
              <th class="py-3.5 px-6">{{ t.colCategory }}</th>
              <th class="py-3.5 px-6">{{ t.colBrand }}</th>
              <th class="py-3.5 px-6">{{ t.colStock }}</th>
              <th class="py-3.5 px-6">{{ t.colPriceUsd }}</th>
              <th class="py-3.5 px-6">{{ t.colPriceBs }}</th>
              <th class="py-3.5 px-6 text-center">状态 / 操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="item in filteredParts" :key="item.oem" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-4 px-6">
                <div class="flex items-center gap-1.5">
                  <template v-if="parseImages(item.image_url).length > 0">
                    <div 
                      @click="$emit('open-gallery', parseImages(item.image_url), 0)"
                      class="w-10 h-10 rounded-xl overflow-hidden border border-slate-200 cursor-pointer hover:scale-105 transition-transform shadow-2xs relative group"
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
              <td class="py-4 px-6 font-mono font-bold text-slate-800">{{ item.oem }}</td>
              <td class="py-4 px-6 font-medium text-slate-900 relative">
                <div class="group relative inline-block max-w-[220px]">
                  <p class="truncate cursor-default text-slate-900">{{ item.name }}</p>
                  <div class="absolute left-0 bottom-full mb-1 hidden group-hover:block z-30 bg-slate-900 text-white text-xs rounded-lg px-3 py-1.5 shadow-xl whitespace-nowrap pointer-events-none">
                    {{ item.name }}
                  </div>
                </div>
              </td>
              <td class="py-4 px-6 text-slate-600">
                <span class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded text-xs font-semibold">{{ item.category || '未分类' }}</span>
              </td>
              <td class="py-4 px-6 text-slate-600">
                <span class="bg-slate-100 px-2.5 py-1 rounded-md text-xs font-medium">{{ item.brand }}</span>
              </td>
              <td class="py-4 px-6 font-bold" :class="item.stock <= 5 ? 'text-rose-600' : 'text-slate-800'">{{ item.stock }}</td>
              <td class="py-4 px-6 font-bold text-blue-600">$ {{ item.price.toFixed(2) }}</td>
              <td class="py-4 px-6 font-bold text-emerald-600">Bs. {{ (item.price * bcvRate).toFixed(2) }}</td>
              <td class="py-4 px-6 text-center">
                <div class="inline-flex items-center justify-center gap-3">
                  <span :class="['inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold whitespace-nowrap',
                    item.stock > 5 ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600']">
                    {{ item.stock > 5 ? '充足' : '库存紧张' }}
                  </span>
                  <button @click="$emit('delete-part', item)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-2.5 py-1 rounded-lg font-medium transition-colors whitespace-nowrap cursor-pointer">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 🌟 子视图 2：仓库货架与库位对照 (Bin Location) -->
    <div v-if="activeSubTab === 'warehouse'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
      <div>
        <h3 class="font-bold text-slate-800 flex items-center gap-2 text-base">
          📦 仓库货架与库位对照 (Bin Location Management)
        </h3>
        <p class="text-xs text-slate-400 mt-1">
          精准定位每个配件在实体仓库中的货架位置（例如: Estante A-1, B-3）
        </p>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-4">配件编码</th>
              <th class="py-3 px-4">{{ t.colOem }}</th>
              <th class="py-3 px-4">配件名称</th>
              <th class="py-3 px-4">适配品牌</th>
              <th class="py-3 px-4">总库存</th>
              <th class="py-3 px-4">货架库位 (BIN LOCATION)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="item in partsList" :key="item.oem" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-3.5 px-4 font-mono text-xs text-slate-400">#{{ item.id || 'N/A' }}</td>
              <td class="py-3.5 px-4 font-mono font-bold text-slate-800">{{ item.oem }}</td>
              <td class="py-3.5 px-4 font-medium text-slate-900">{{ item.name }}</td>
              <td class="py-3.5 px-4">
                <span class="bg-slate-100 px-2 py-0.5 rounded text-xs font-medium text-slate-600">{{ item.brand }}</span>
              </td>
              <td class="py-3.5 px-4 font-bold" :class="item.stock <= 5 ? 'text-rose-600' : 'text-slate-800'">
                {{ item.stock }}
              </td>
              <td class="py-3.5 px-4">
                <div class="inline-flex items-center gap-1.5 bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-lg text-xs font-semibold font-mono border border-emerald-200/60">
                  <span>📍 {{ item.bin_location || 'Estante A-1' }}</span>
                  <span class="text-[10px] text-emerald-600 font-normal">(默认主货架)</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Plus } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiUrl } from '../utils/api'

const props = defineProps({
  partsList: Array,
  searchQuery: String,
  selectedBrand: String,
  brandsList: Array,
  bcvRate: Number
})

const emit = defineEmits(['update:searchQuery', 'update:selectedBrand', 'open-add-modal', 'open-gallery', 'delete-part'])
const { t } = useI18n()

// 🌟 子视图状态切换：stock（商品库存） / warehouse（仓库库位）
const activeSubTab = ref('stock')

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
    if (!query) return matchBrand

    const cleanOem = i.oem ? i.oem.toLowerCase().replace(/[^a-z0-9]/g, '') : ''
    const cleanName = i.name ? i.name.toLowerCase() : ''
    const cleanBrand = i.brand ? i.brand.toLowerCase() : ''
    const rawOem = i.oem ? i.oem.toLowerCase() : ''
    const rawName = i.name ? i.name.toLowerCase() : ''

    const matchSearch = 
      cleanOem.includes(cleanQuery) || 
      rawOem.includes(query) || 
      cleanName.includes(query) ||
      rawName.includes(query) ||
      cleanBrand.includes(query)

    return matchBrand && matchSearch
  })
})
</script>