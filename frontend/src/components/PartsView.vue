<!-- src/components/PartsView.vue -->
<template>
  <div class="space-y-6">
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
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
              :class="['px-3 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0', selectedBrand === b ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
            >
              {{ b === 'ALL' ? t.allBrands : b }}
            </button>
          </div>
        </div>

        <button
          @click="$emit('open-add-modal')"
          class="w-full md:w-auto flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md shadow-blue-500/25 transition-all"
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
              <!-- 单图预览主图，点击无缝唤起大图画廊 -->
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
              
              <!-- 🌟 优化后的配件名称列：长名称自动截断省略，鼠标悬停时自动浮现完整内容 -->
              <td class="py-4 px-6 font-medium text-slate-900 relative">
                <div class="group relative inline-block max-w-[220px]">
                  <p class="truncate cursor-default text-slate-900">{{ item.name }}</p>
                  <!-- 悬停时浮现的高级气泡提示框 -->
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
                  <button @click="$emit('delete-part', item)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-2.5 py-1 rounded-lg font-medium transition-colors whitespace-nowrap">
                    删除
                  </button>
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
import { computed } from 'vue'
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

// 解析多张图片数组
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

// 🌟 升级版前端智能过滤：自动清洗两边的空格和特殊符号再比对
const filteredParts = computed(() => {
  const query = props.searchQuery ? props.searchQuery.trim().toLowerCase() : ''
  // 核心清洗：把用户输入的查询词去掉所有空格、横线、斜杠
  const cleanQuery = query.replace(/[^a-z0-9]/g, '')

  return props.partsList.filter(i => {
    const matchBrand = props.selectedBrand === 'ALL' || i.brand === props.selectedBrand
    
    if (!query) return matchBrand

    // 把数据库里的 oem、name、brand 也进行相同规则的清洗
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