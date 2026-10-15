<!-- src/components/QuotationsView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部 Tab 页签切换栏 -->
    <div class="flex items-center justify-between bg-white px-6 py-3 rounded-2xl border border-slate-200/80 shadow-xs">
      <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
        <button 
          @click="activeSubTab = 'history'"
          :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', 
            activeSubTab === 'history' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
        >
          📄 历史报价单据归档
        </button>
        <button 
          @click="$emit('navigate', 'desk')"
          class="px-4 py-2 rounded-lg text-xs font-bold text-slate-600 hover:text-slate-900 transition-all cursor-pointer flex items-center gap-1.5"
        >
          <span>⚡ 进入快速开单报价台 (POS)</span>
        </button>
      </div>

      <div class="flex items-center gap-3">
        <button 
          @click="$emit('export-quotations')" 
          class="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-2xs"
        >
          📊 导出历史报价 Excel
        </button>
        <button 
          @click="$emit('download-pdf')" 
          class="bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-2xs"
        >
          📥 下载最近 PDF 凭证
        </button>
      </div>
    </div>

    <!-- 🌟 历史报价单据列表表格 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-4 md:p-6 border-b border-slate-100">
        <h3 class="font-bold text-slate-900 text-base">历史报价与销售凭证管理</h3>
        <p class="text-xs text-slate-500 mt-0.5">查阅、打印或删除过去的报价明细，支持一键导出 Excel 及 PDF</p>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-6">报价单号 / ID</th>
              <th class="py-3.5 px-6">客户名称</th>
              <th class="py-3.5 px-6">支付渠道</th>
              <th class="py-3.5 px-6">总金额 (USD)</th>
              <th class="py-3.5 px-6">折合金额 (Bs.)</th>
              <th class="py-3.5 px-6">创建时间</th>
              <th class="py-3.5 px-6 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="quotationsList.length === 0">
              <td colspan="7" class="text-center py-12 text-slate-400 text-xs">
                暂无历史报价记录
              </td>
            </tr>
            <tr v-for="q in quotationsList" :key="q.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-4 px-6 font-mono font-bold text-slate-800">#{{ q.id }}</td>
              <td class="py-4 px-6 font-medium text-slate-900">{{ q.client_name || 'Cliente General' }}</td>
              <td class="py-4 px-6">
                <span class="bg-blue-50 text-blue-600 px-2.5 py-1 rounded-md text-xs font-semibold">{{ q.payment_method || 'Cash_USD' }}</span>
              </td>
              <td class="py-4 px-6 font-bold text-blue-600">$ {{ (q.total_usd || 0).toFixed(2) }}</td>
              <td class="py-4 px-6 font-bold text-emerald-600">Bs. {{ ((q.total_usd || 0) * (q.bcv_rate || 36)).toFixed(2) }}</td>
              <td class="py-4 px-6 text-slate-500 text-xs font-mono">{{ q.created_at || '刚刚' }}</td>
              <td class="py-4 px-6 text-center">
                <div class="inline-flex items-center justify-center gap-2">
                  <button @click="$emit('download-pdf', q)" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg font-medium transition-colors cursor-pointer">
                    📥 PDF
                  </button>
                  <button @click="$emit('delete-quote', q)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-medium transition-colors cursor-pointer">
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
import { ref } from 'vue'

const props = defineProps({
  quotationsList: Array
})

defineEmits(['export-quotations', 'download-pdf', 'delete-quote', 'navigate'])

const activeSubTab = ref('history')
</script>