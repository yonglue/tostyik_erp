<!-- src/components/QuotationListView.vue -->
<template>
  <div class="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
    <div class="flex items-center justify-between bg-white/70 backdrop-blur-xl p-6 rounded-3xl border border-white/60 shadow-sm">
      <div>
        <h2 class="text-2xl font-black text-slate-900 flex items-center gap-2">📄 历史报价单管理</h2>
        <p class="text-sm text-slate-500 font-medium mt-1">查看历史报价，或一键将报价转入 POS 收银台进行结算。</p>
      </div>
    </div>

    <div class="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs font-extrabold uppercase tracking-wider">
            <th class="py-4 px-6">报价单号</th>
            <th class="py-4 px-6">客户名称</th>
            <th class="py-4 px-6 text-right">总金额 (USD)</th>
            <th class="py-4 px-6 text-right">总金额 (Bs.)</th>
            <th class="py-4 px-6 text-center">操作</th>
          </tr>
        </thead>
        <tbody class="text-sm font-medium">
          <tr v-for="q in quotations" :key="q.id" class="border-b border-slate-100 hover:bg-blue-50/40 transition-colors">
            <td class="py-4 px-6 font-mono font-black text-blue-600">{{ q.quotation_no }}</td>
            <td class="py-4 px-6 text-slate-900 font-bold">👤 {{ q.client_name }}</td>
            <td class="py-4 px-6 text-right font-mono font-black text-emerald-600">${{ q.total_usd.toFixed(2) }}</td>
            <td class="py-4 px-6 text-right font-mono font-bold text-slate-600">Bs. {{ q.total_bs.toFixed(2) }}</td>
            <td class="py-4 px-6 text-center">
              <div class="flex items-center justify-center gap-2">
                <button 
                  @click="downloadPdf(q.quotation_no)"
                  class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition-all shadow-2xs"
                >
                  📄 下载PDF
                </button>
                <button 
                  @click="convertToPos(q)"
                  class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1"
                >
                  🚀 转入POS开单
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="quotations.length === 0">
            <td colspan="5" class="text-center py-20 text-slate-400 font-bold">
              <span class="text-4xl block mb-3">📭</span>
              暂无历史报价单
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../utils/api'

const emit = defineEmits(['convert-to-pos', 'show-toast'])

const quotations = ref([])

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
    emit('show-toast', '✅ PDF 下载成功', 'success')
  } catch (err) {
    console.error(err)
    emit('show-toast', '❌ PDF 下载失败', 'error')
  }
}

const convertToPos = (q) => {
  try {
    // 解析存着的 JSON 字符串
    const items = JSON.parse(q.items_json)
    emit('convert-to-pos', { client_name: q.client_name, items })
  } catch (e) {
    console.error('解析报价单明细失败', e)
    emit('show-toast', '❌ 解析报价单数据失败', 'error')
  }
}

onMounted(() => {
  fetchQuotations()
})
</script>