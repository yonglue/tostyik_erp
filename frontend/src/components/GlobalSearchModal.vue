<!-- src/components/GlobalSearchModal.vue -->
<template>
  <div v-if="visible" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-start justify-center pt-[15vh] z-[100]" @click.self="$emit('close')">
    <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden border border-slate-200/80 flex flex-col animate-in zoom-in-95 duration-150 mx-4">
      
      <!-- 搜索输入框 -->
      <div class="flex items-center px-4 py-3 border-b border-slate-100">
        <Search class="text-slate-400 mr-3" :size="20" />
        <input 
          ref="searchInputRef"
          v-model="searchQuery"
          type="text"
          placeholder="搜索商品 OEM/名称，或客户姓名..."
          class="w-full bg-transparent text-slate-800 text-base outline-none placeholder:text-slate-400 font-medium"
          @keydown.down.prevent="moveSelection(1)"
          @keydown.up.prevent="moveSelection(-1)"
          @keydown.enter.prevent="executeSelection"
        />
        <kbd class="hidden sm:inline-flex items-center gap-1 px-2 py-1 bg-slate-100 border border-slate-200 rounded text-[10px] font-mono text-slate-500 font-bold ml-2">
          ESC
        </kbd>
      </div>

      <!-- 搜索结果区 -->
      <div class="max-h-[60vh] overflow-y-auto custom-scrollbar p-2">
        
        <!-- 商品结果 -->
        <div v-if="filteredParts.length > 0">
          <div class="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider">商品库存</div>
          <div 
            v-for="(part, index) in filteredParts" 
            :key="part.id"
            @click="selectItem('part', part)"
            @mouseenter="selectedIndex = index"
            :class="[
              'flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-colors',
              selectedIndex === index ? 'bg-blue-50 border border-blue-100' : 'border border-transparent hover:bg-slate-50'
            ]"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                <Package :size="16" />
              </div>
              <div>
                <p class="text-sm font-bold text-slate-800">{{ part.name }}</p>
                <p class="text-xs font-mono text-slate-500">{{ part.oem }} <span class="text-slate-300 mx-1">|</span> 库存: {{ part.stock }}</p>
              </div>
            </div>
            <span class="text-sm font-mono font-bold text-blue-600">${{ Number(part.price || 0).toFixed(2) }}</span>
          </div>
        </div>

        <!-- 客户结果 -->
        <div v-if="filteredClients.length > 0">
          <div class="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider mt-2">客户档案</div>
          <div 
            v-for="(client, index) in filteredClients" 
            :key="client.id"
            @click="selectItem('client', client)"
            @mouseenter="selectedIndex = filteredParts.length + index"
            :class="[
              'flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-colors',
              selectedIndex === (filteredParts.length + index) ? 'bg-blue-50 border border-blue-100' : 'border border-transparent hover:bg-slate-50'
            ]"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                <User :size="16" />
              </div>
              <div>
                <p class="text-sm font-bold text-slate-800">{{ client.name }}</p>
                <p class="text-xs font-mono text-slate-500">{{ client.rif_or_cedula || '无 RIF' }}</p>
              </div>
            </div>
            <span class="text-xs font-bold" :class="(client.debt || 0) > 0 ? 'text-rose-500' : 'text-slate-400'">
              欠款: ${{ (client.debt || 0).toFixed(2) }}
            </span>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="searchQuery && filteredParts.length === 0 && filteredClients.length === 0" class="text-center py-12 text-slate-400 text-sm">
          <span class="text-3xl block mb-2">🔍</span>
          没有找到与 "{{ searchQuery }}" 相关的商品或客户
        </div>
        <div v-else-if="!searchQuery" class="text-center py-12 text-slate-400 text-sm">
          <span class="text-3xl block mb-2">⌨️</span>
          请输入商品 OEM、名称或客户姓名开始搜索...
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="bg-slate-50 px-4 py-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-medium">
        <div class="flex items-center gap-4">
          <span class="flex items-center gap-1"><kbd class="bg-white border px-1.5 py-0.5 rounded">↑</kbd> <kbd class="bg-white border px-1.5 py-0.5 rounded">↓</kbd> 选择</span>
          <span class="flex items-center gap-1"><kbd class="bg-white border px-1.5 py-0.5 rounded">↵</kbd> 确认</span>
        </div>
        <span>全局搜索 (Ctrl + K)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Search, Package, User } from 'lucide-vue-next'

const props = defineProps({
  visible: Boolean,
  partsList: Array,
  clientsList: Array
})

const emit = defineEmits(['close', 'select'])

const searchQuery = ref('')
const selectedIndex = ref(0)
const searchInputRef = ref(null)

const filteredParts = computed(() => {
  if (!searchQuery.value.trim()) return []
  const q = searchQuery.value.toLowerCase().trim()
  return props.partsList.filter(p => 
    p.oem.toLowerCase().includes(q) || p.name.toLowerCase().includes(q)
  ).slice(0, 5) // 最多显示 5 个商品
})

const filteredClients = computed(() => {
  if (!searchQuery.value.trim()) return []
  const q = searchQuery.value.toLowerCase().trim()
  return props.clientsList.filter(c => 
    c.name.toLowerCase().includes(q) || (c.rif_or_cedula && c.rif_or_cedula.toLowerCase().includes(q))
  ).slice(0, 5) // 最多显示 5 个客户
})

const flatResults = computed(() => {
  return [
    ...filteredParts.value.map(p => ({ type: 'part', item: p })),
    ...filteredClients.value.map(c => ({ type: 'client', item: c }))
  ]
})

// 监听弹窗打开，重置状态并自动聚焦
watch(() => props.visible, async (newVal) => {
  if (newVal) {
    searchQuery.value = ''
    selectedIndex.value = 0
    await nextTick()
    if (searchInputRef.value) searchInputRef.value.focus()
  }
})

// 监听搜索结果变化，重置高亮索引
watch([filteredParts, filteredClients], () => {
  selectedIndex.value = 0
})

const moveSelection = (step) => {
  if (flatResults.value.length === 0) return
  selectedIndex.value = (selectedIndex.value + step + flatResults.value.length) % flatResults.value.length
}

const executeSelection = () => {
  if (flatResults.value.length === 0) return
  const selected = flatResults.value[selectedIndex.value]
  if (selected) {
    selectItem(selected.type, selected.item)
  }
}

const selectItem = (type, item) => {
  emit('select', { type, item })
  emit('close')
}

const handleKeydown = (e) => {
  if (!props.visible) return
  if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
/* 隐藏原生滚动条，使用你项目的幽灵滚动条 */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(203, 213, 225, 0.6); border-radius: 10px; }
</style>