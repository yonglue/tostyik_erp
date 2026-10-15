<!-- src/components/QuotationsView.vue -->
<template>
  <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
    <div class="p-4 md:p-6 border-b border-slate-100 flex items-center justify-between">
      <p class="text-sm text-slate-500 font-medium">{{ t.quotationSubTitle }}</p>
      <button
        @click="$emit('export-quotations')"
        class="flex items-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md transition-all"
      >
        <FileSpreadsheet :size="16" />
        <span>{{ t.exportExcelBtn }}</span>
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse min-w-[750px]">
        <thead>
          <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <th class="py-3.5 px-6">{{ t.qNo }}</th>
            <th class="py-3.5 px-6">{{ t.qTime }}</th>
            <th class="py-3.5 px-6">{{ t.qClient }}</th>
            <th class="py-3.5 px-6">{{ t.qTotalUsd }}</th>
            <th class="py-3.5 px-6">{{ t.qTotalBs }}</th>
            <th class="py-3.5 px-6">{{ t.qRate }}</th>
            <th class="py-3.5 px-6 text-center">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 text-sm">
          <tr v-for="q in quotationsList" :key="q.id" class="hover:bg-slate-50/50 transition-colors">
            <td class="py-4 px-6 font-mono font-bold text-blue-600">{{ q.quotation_no }}</td>
            <td class="py-4 px-6 text-slate-500 text-xs">{{ q.timestamp }}</td>
            <td class="py-4 px-6 font-medium text-slate-900">{{ q.client_name }}</td>
            <td class="py-4 px-6 font-bold text-slate-800">$ {{ q.total_usd.toFixed(2) }}</td>
            <td class="py-4 px-6 font-bold text-emerald-600">Bs. {{ q.total_bs.toFixed(2) }}</td>
            <td class="py-4 px-6 text-slate-600 font-mono">1 = {{ q.bcv_rate }}</td>
            <td class="py-4 px-6 text-center space-x-2">
              <button @click="$emit('download-pdf')" class="text-xs bg-slate-100 hover:bg-blue-50 text-blue-600 px-3 py-1.5 rounded-lg font-medium transition-colors">
                {{ t.downloadAgain }}
              </button>
              <button @click="$emit('delete-quote', q)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-medium transition-colors">
                {{ t.btnDelete }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'

defineProps({
  quotationsList: Array
})

defineEmits(['export-quotations', 'download-pdf', 'delete-quote'])
const { t } = useI18n()
</script>