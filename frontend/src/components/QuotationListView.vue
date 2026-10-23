<!-- src/components/QuotationListView.vue -->
<template>
  <div class="max-w-11xl mx-auto space-y-6 animate-in fade-in duration-300 pb-24">
    
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
                    :disabled="q.converted_order_id"
                    :class="{ 'opacity-40 cursor-not-allowed': q.converted_order_id }"
                    class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1 cursor-pointer"
                  >
                    {{ q.converted_order_id ? `✅ ${tExt.btnConvert} #${q.converted_order_id}` : tExt.btnConvert }}
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
        <!-- 基本信息卡片 (重构为规整网格) -->
        <div class="bg-slate-50/50 p-4 rounded-2xl border border-slate-100 grid grid-cols-2 gap-4 text-sm">
          <div class="col-span-2 pb-3 border-b border-slate-200/60">
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colQuoteNo }}</p>
            <p class="font-mono text-lg font-black text-blue-600">{{ currentQuote.quotation_no }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colClient }}</p>
            <p class="font-bold text-slate-800">👤 {{ currentQuote.client_name }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colTotalUsd }}</p>
            <p class="font-mono text-xl font-black text-emerald-600">$ {{ Number(currentQuote.total_usd || 0).toFixed(2) }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colTotalBs }}</p>
            <p class="font-mono text-lg font-black text-slate-700">Bs. {{ Number(currentQuote.total_bs || 0).toFixed(2) }}</p>
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

      <!-- Drawer 底部操作区 (统一排版) -->
      <template #footer>
        <div class="px-6 py-4 border-t border-slate-100 flex items-center justify-between gap-3 bg-slate-50/50">
          <!-- 左侧删除 -->
          <button 
            @click="onDeleteFromDrawer" 
            class="px-5 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl text-xs font-bold transition-colors cursor-pointer"
          >
            🗑️ {{ t.common.delete }}
          </button>
          
          <!-- 右侧操作组 -->
          <div class="flex items-center gap-3">
            <button 
              @click="downloadPdf(currentQuote.quotation_no)" 
              class="px-5 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer flex items-center gap-1"
            >
              📄 {{ tExt.btnDownload }}
            </button>
            <button 
              @click="printA4Quotation(currentQuote)" 
              class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md transition-colors cursor-pointer flex items-center gap-1"
            >
              🖨️ 打印 A4 报价单
            </button>
            <button 
              @click="convertToPos(currentQuote)" 
              :disabled="currentQuote.converted_order_id"
              :class="{ 'opacity-40 cursor-not-allowed': currentQuote.converted_order_id }"
              class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20 transition-colors cursor-pointer flex items-center gap-1"
            >
              🚀 {{ currentQuote.converted_order_id ? `✅ ${tExt.btnConvert} #${currentQuote.converted_order_id}` : tExt.btnConvert }}
            </button>
          </div>
        </div>
      </template>
    </SideDrawer>

  </div>

  <!-- ==================================================== -->
  <!-- 🌟 核心新增：隐藏的 A4 报价单打印区域                  -->
  <!-- ==================================================== -->
  <Teleport to="body">
    <div v-if="a4PrintData" class="a4-print-only" id="a4-print-section">
      <div class="a4-header">
        <div class="company-info">
          <h1>TOSTIYK (TK)</h1>
          <p>RIF: J-31234567-8</p>
          <p>Valera, Estado Trujillo - Venezuela</p>
          <p>Tel: +58 412-0000000</p>
        </div>
        <div class="document-info">
          <h2>报价单</h2>
          <p><strong>单号:</strong> {{ a4PrintData.quotation_no }}</p>
          <p><strong>日期:</strong> {{ new Date(a4PrintData.created_at || Date.now()).toLocaleDateString() }}</p>
        </div>
      </div>

      <div class="a4-parties">
        <div class="client-box">
          <h3>客户信息</h3>
          <p><strong>名称:</strong> {{ a4PrintData.client_name }}</p>
          <p><strong>报价状态:</strong> 有效报价</p>
        </div>
      </div>

      <table class="a4-table">
        <thead>
          <tr>
            <th width="5%">#</th>
            <th width="40%">商品名称 / 描述</th>
            <th width="20%">OEM 编号</th>
            <th width="10%">数量</th>
            <th width="12%">单价 (USD)</th>
            <th width="13%">小计 (USD)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in parsedA4Items" :key="index">
            <td>{{ index + 1 }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.oem }}</td>
            <td>{{ item.quantity }}</td>
            <td>${{ Number(item.price || 0).toFixed(2) }}</td>
            <td>${{ Number((item.quantity * item.price) || 0).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>

      <div class="a4-totals">
        <div class="total-box">
          <p>总计金额 (USD): <strong>${{ Number(a4PrintData.total_usd || 0).toFixed(2) }}</strong></p>
          <p>总计金额 (VES): <strong>Bs. {{ Number(a4PrintData.total_bs || 0).toFixed(2) }}</strong></p>
        </div>
      </div>

      <div class="a4-footer-note">
        <p>备注：此报价单有效期 7 天，逾期价格可能随市场/汇率波动有所调整，敬请谅解。</p>
      </div>

      <div class="a4-signatures">
        <div class="sign-box">
          <p>客户确认签字:</p>
          <div class="sign-line"></div>
        </div>
        <div class="sign-box">
          <p>销售员签字 / 盖章:</p>
          <div class="sign-line"></div>
        </div>
      </div>
    </div>
  </Teleport>
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
const drawerVisible = ref(false)
const currentQuote = ref(null)

// 🌟 A4 打印专用状态
const a4PrintData = ref(null)

const parsedItems = computed(() => {
  if (!currentQuote.value?.items_json) return []
  try { return JSON.parse(currentQuote.value.items_json) } catch (e) { return [] }
})

const parsedA4Items = computed(() => {
  if (!a4PrintData.value?.items_json) return []
  try { return JSON.parse(a4PrintData.value.items_json) } catch (e) { return [] }
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
    const res = await apiFetch(`/api/quotation/pdf/download?quotation_no=${quotationNo}&lang=${currentLang.value}`)
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
    emit('convert-to-pos', { id: q.id, client_name: q.client_name, items })
    closeDrawer()
  } catch (e) {
    console.error('解析报价单明细失败', e)
    emit('show-toast', '❌ ' + tExt.value.toastParseFail, 'error')
  }
}

const onDeleteFromDrawer = () => {
  emit('delete-quote', currentQuote.value)
  closeDrawer()
}

// 🌟 A4 打印触发逻辑
const printA4Quotation = (quote) => {
  if (!quote) return
  a4PrintData.value = quote
  setTimeout(() => {
    window.print()
    setTimeout(() => { a4PrintData.value = null }, 1000)
  }, 100)
}

onMounted(() => {
  fetchQuotations()
})
</script>

<style>
/* 🌟 屏幕端隐藏打印区域 */
@media screen {
  .a4-print-only {
    display: none !important;
  }
}

/* 🌟 打印端专属样式 */
@media print {
  body > * {
    display: none !important;
  }
  
  #a4-print-section {
    display: block !important;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 20mm;
    background: white;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #000;
  }

  @page {
    margin: 0;
  }

  .a4-header {
    display: flex;
    justify-content: space-between;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
    margin-bottom: 20px;
  }
  .company-info h1 { font-size: 24px; margin: 0 0 5px 0; }
  .company-info p { font-size: 12px; margin: 2px 0; color: #555; }
  
  .document-info { text-align: right; }
  .document-info h2 { font-size: 20px; margin: 0 0 10px 0; text-transform: uppercase; }
  .document-info p { font-size: 13px; margin: 4px 0; }

  .a4-parties { margin-bottom: 20px; }
  .client-box { border: 1px solid #ccc; padding: 10px; border-radius: 4px; }
  .client-box h3 { font-size: 14px; margin: 0 0 8px 0; border-bottom: 1px solid #eee; padding-bottom: 4px; }
  .client-box p { font-size: 13px; margin: 4px 0; }

  .a4-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
  }
  .a4-table th, .a4-table td {
    border: 1px solid #333;
    padding: 8px;
    font-size: 12px;
  }
  .a4-table th {
    background-color: #f0f0f0;
    font-weight: bold;
    text-align: left;
  }
  
  .a4-totals {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;
  }
  .total-box {
    width: 300px;
    border-top: 2px solid #333;
    padding-top: 10px;
  }
  .total-box p {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    margin: 5px 0;
  }

  .a4-footer-note {
    font-size: 11px;
    color: #666;
    margin-bottom: 40px;
    border-bottom: 1px dashed #ccc;
    padding-bottom: 10px;
  }

  .a4-signatures {
    display: flex;
    justify-content: space-between;
    margin-top: 60px;
  }
  .sign-box {
    width: 200px;
    text-align: center;
  }
  .sign-box p { font-size: 13px; font-weight: bold; margin-bottom: 40px; }
  .sign-line { border-bottom: 1px solid #333; }
}
</style>