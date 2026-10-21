<!-- src/components/QuotationListView.vue -->
<template>
  <div class="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
    
    <!-- 顶部标题栏 -->
    <div class="flex items-center justify-between bg-white/70 backdrop-blur-xl p-6 rounded-3xl border border-white/60 shadow-sm">
      <div>
        <h2 class="text-2xl font-black text-slate-900 flex items-center gap-2">
          <span>📄</span> {{ tExt.title }}
        </h2>
        <p class="text-sm text-slate-500 font-medium mt-1">{{ tExt.subtitle }}</p>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs font-extrabold uppercase tracking-wider">
              <th class="py-4 px-6">{{ tExt.colQuoteNo }}</th>
              <th class="py-4 px-6">{{ tExt.colClient }}</th>
              <th class="py-4 px-6 text-right">{{ tExt.colTotalUsd }}</th>
              <th class="py-4 px-6 text-right">{{ tExt.colTotalBs }}</th>
              <th class="py-4 px-6 text-center">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="text-sm font-medium">
            <tr 
              v-for="q in quotations" 
              :key="q.id" 
              @click="openDrawer(q)"
              class="border-b border-slate-100 hover:bg-blue-50/40 transition-colors cursor-pointer group"
            >
              <td class="py-4 px-6 font-mono font-black text-blue-600 group-hover:text-blue-700 transition-colors">
                {{ q.quotation_no }}
              </td>
              <td class="py-4 px-6 text-slate-900 font-bold">👤 {{ q.client_name }}</td>
              <td class="py-4 px-6 text-right font-mono font-black text-emerald-600">
                ${{ Number(q.total_usd || 0).toFixed(2) }}
              </td>
              <td class="py-4 px-6 text-right font-mono font-bold text-slate-600">
                Bs. {{ Number(q.total_bs || 0).toFixed(2) }}
              </td>
              <td class="py-4 px-6 text-center" @click.stop>
                <div class="flex items-center justify-center gap-2">
                  <button 
                    @click="openDrawer(q)"
                    class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition-all shadow-2xs cursor-pointer"
                  >
                    {{ tExt.btnDetail }}
                  </button>
                  <button 
                    @click="downloadPdf(q.quotation_no)"
                    class="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200/60 rounded-lg text-xs font-bold transition-all shadow-2xs cursor-pointer flex items-center gap-1"
                  >
                    📄 {{ tExt.btnDownload }}
                  </button>
                  <button 
                    @click="convertToPos(q)"
                    class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1 cursor-pointer"
                  >
                    🚀 {{ tExt.btnConvert }}
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="quotations.length === 0">
              <td colspan="5" class="text-center py-20 text-slate-400 font-bold">
                <span class="text-4xl block mb-3">📭</span>
                {{ tExt.emptyData }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 🌟 右侧报价单详情 Drawer -->
    <SideDrawer 
      :visible="drawerVisible" 
      :title="tExt.drawerTitle" 
      icon="📄"
      @close="closeDrawer"
    >
      <div class="p-6 space-y-6" v-if="currentQuote">
        <!-- 基本信息卡片 -->
        <div class="grid grid-cols-2 gap-4 bg-slate-50/50 p-4 rounded-2xl border border-slate-100">
          <div class="col-span-2">
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colQuoteNo }}</p>
            <p class="font-mono text-lg font-black text-blue-600">{{ currentQuote.quotation_no }}</p>
          </div>
          <div class="col-span-2">
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colClient }}</p>
            <p class="font-bold text-slate-800 text-base">👤 {{ currentQuote.client_name }}</p>
          </div>
          <div class="border-t border-slate-200/60 pt-3">
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colTotalUsd }}</p>
            <p class="font-mono text-xl font-black text-emerald-600">$ {{ Number(currentQuote.total_usd || 0).toFixed(2) }}</p>
          </div>
          <div class="border-t border-slate-200/60 pt-3">
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colTotalBs }}</p>
            <p class="font-mono text-xl font-black text-slate-700">Bs. {{ Number(currentQuote.total_bs || 0).toFixed(2) }}</p>
          </div>
        </div>

        <!-- 商品明细 -->
        <div class="space-y-3">
          <h4 class="text-sm font-bold text-slate-800 border-b border-slate-200 pb-2 flex justify-between">
            <span>{{ tExt.itemsTitle }}</span>
            <span class="text-xs text-slate-400 font-normal">{{ parsedItems.length }} SKUs</span>
          </h4>
          <div class="space-y-2 max-h-[40vh] overflow-y-auto pr-1">
            <div 
              v-for="(item, idx) in parsedItems" 
              :key="idx" 
              class="flex justify-between items-center bg-white border border-slate-100 p-3 rounded-xl shadow-2xs hover:border-blue-200 transition-colors"
            >
              <div class="flex-1 min-w-0 pr-3">
                <p class="font-bold text-slate-800 text-sm truncate">{{ item.name }}</p>
                <p class="text-[11px] font-mono text-slate-500 mt-0.5">{{ item.oem }}</p>
              </div>
              <div class="text-right shrink-0">
                <p class="font-mono text-xs text-slate-500">{{ item.quantity }} × ${{ Number(item.price || 0).toFixed(2) }}</p>
                <p class="font-mono font-bold text-slate-900 text-sm mt-0.5">${{ (item.quantity * item.price).toFixed(2) }}</p>
              </div>
            </div>
            <div v-if="parsedItems.length === 0" class="text-center py-6 text-slate-400 text-xs">
              {{ tExt.noItems }}
            </div>
          </div>
        </div>
      </div>

      <!-- Drawer 底部操作区 -->
      <template #footer>
        <div class="px-6 py-4 border-t border-slate-100 flex items-center justify-between gap-3 bg-slate-50/50">
          <button 
            @click="onDeleteFromDrawer" 
            class="px-4 py-2.5 text-rose-600 hover:text-rose-700 font-bold text-xs transition-colors cursor-pointer"
          >
            🗑️ {{ t.common.delete }}
          </button>
          <div class="flex gap-3">
            <button 
              @click="downloadPdf(currentQuote.quotation_no)" 
              class="px-5 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1"
            >
              📄 {{ tExt.btnDownload }}
            </button>
            <button 
              @click="convertToPos(currentQuote)" 
              class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20 transition-colors cursor-pointer flex items-center gap-1"
            >
              🚀 {{ tExt.btnConvert }}
            </button>
          </div>
        </div>
      </template>
    </SideDrawer>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '../utils/api'
import { useI18n } from '../composables/useI18n'
import SideDrawer from './SideDrawer.vue'

const emit = defineEmits(['convert-to-pos', 'show-toast', 'delete-quote'])
const { t, currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '历史报价单管理' : isEs ? 'Historial de Cotizaciones' : 'Quotation History',
    subtitle: isZh ? '查看历史报价明细，或一键转入 POS 收银台进行结算。' : isEs ? 'Vea detalles o convierta a Caja POS.' : 'View details or convert to POS.',
    colQuoteNo: isZh ? '报价单号' : isEs ? 'Nro. Cotización' : 'Quote No.',
    colClient: isZh ? '客户名称' : isEs ? 'Cliente' : 'Client Name',
    colTotalUsd: isZh ? '总金额 (USD)' : isEs ? 'Total (USD)' : 'Total (USD)',
    colTotalBs: isZh ? '总金额 (Bs.)' : isEs ? 'Total (Bs.)' : 'Total (Bs.)',
    emptyData: isZh ? '暂无历史报价单' : isEs ? 'No hay cotizaciones registradas' : 'No quotations found',
    btnDetail: isZh ? '详情' : isEs ? 'Detalle' : 'Detail',
    btnDownload: isZh ? '下载 PDF' : isEs ? 'Descargar PDF' : 'Download PDF',
    btnConvert: isZh ? '转入 POS' : isEs ? 'A Caja POS' : 'To POS',
    drawerTitle: isZh ? '报价单详情' : isEs ? 'Detalle de Cotización' : 'Quotation Details',
    itemsTitle: isZh ? '商品明细' : isEs ? 'Detalle de Productos' : 'Item Details',
    noItems: isZh ? '无商品明细记录' : isEs ? 'Sin detalles de productos' : 'No item details',
    toastDownloadSuccess: isZh ? 'PDF 下载成功' : isEs ? 'PDF descargado con éxito' : 'PDF downloaded successfully',
    toastDownloadFail: isZh ? 'PDF 获取失败' : isEs ? 'Error al obtener PDF' : 'Failed to fetch PDF',
    toastParseFail: isZh ? '解析报价单数据失败' : isEs ? 'Error al analizar datos' : 'Failed to parse data'
  }
})

const quotations = ref([])

// Drawer 状态
const drawerVisible = ref(false)
const currentQuote = ref(null)

const parsedItems = computed(() => {
  if (!currentQuote.value?.items_json) return []
  try {
    return JSON.parse(currentQuote.value.items_json)
  } catch (e) {
    return []
  }
})

const fetchQuotations = async () => {
  try {
    const res = await apiFetch('/api/quotations')
    if (res.ok) {
      quotations.value = await res.json()
    }
  } catch (e) {
    console.error('获取报价单列表失败', e)
  }
}

const openDrawer = (q) => {
  currentQuote.value = q
  drawerVisible.value = true
}

const closeDrawer = () => {
  drawerVisible.value = false
  currentQuote.value = null
}

const downloadPdf = async (quotationNo) => {
  try {
    const res = await apiFetch(`/api/quotation/pdf/download?quotation_no=${quotationNo}`)
    if (!res.ok) throw new Error('PDF 获取失败')
    
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Quotation_${quotationNo}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
    emit('show-toast', '✅ ' + tExt.value.toastDownloadSuccess, 'success')
  } catch (err) {
    console.error(err)
    emit('show-toast', '❌ ' + tExt.value.toastDownloadFail, 'error')
  }
}

const convertToPos = (q) => {
  try {
    const items = JSON.parse(q.items_json)
    emit('convert-to-pos', { client_name: q.client_name, items })
    closeDrawer() // 转入 POS 后关闭抽屉
  } catch (e) {
    console.error('解析报价单明细失败', e)
    emit('show-toast', '❌ ' + tExt.value.toastParseFail, 'error')
  }
}

const onDeleteFromDrawer = () => {
  emit('delete-quote', currentQuote.value)
  closeDrawer()
}

onMounted(() => {
  fetchQuotations()
})
</script>