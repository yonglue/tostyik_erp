<!-- src/components/TransactionsView.vue -->
<template>
  <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
    <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
      <p class="text-sm text-slate-500 font-medium">{{ t.transSubTitle }}</p>
      <div class="flex items-center gap-3 w-full md:w-auto">
        <button
          @click="$emit('export-transactions')"
          class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md transition-all"
        >
          <FileSpreadsheet :size="16" />
          <span>{{ t.exportExcelBtn }}</span>
        </button>
        <button
          @click="$emit('open-tx-modal')"
          class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md shadow-emerald-500/25 transition-all"
        >
          <Plus :size="16" />
          <span>{{ t.newTransBtn }}</span>
        </button>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse min-w-[850px]">
        <thead>
          <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <th class="py-3.5 px-6">{{ t.txTime }}</th>
            <th class="py-3.5 px-6">{{ t.colCode }}</th>
            <th class="py-3.5 px-6">{{ t.colName }}</th>
            <th class="py-3.5 px-6 text-center">{{ t.txType }}</th>
            <th class="py-3.5 px-6">{{ t.txQty }}</th>
            <th class="py-3.5 px-6">{{ t.txUnitPrice }}</th>
            <th class="py-3.5 px-6">{{ t.txTotal }}</th>
            <th class="py-3.5 px-6">{{ t.txTarget }}</th>
            <th class="py-3.5 px-6 text-center">{{ t.colActions || '操作' }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 text-sm">
          <tr v-for="tx in transactionsList" :key="tx.id" class="hover:bg-slate-50/50 transition-colors">
            <td class="py-4 px-6 text-slate-500 text-xs">{{ tx.timestamp }}</td>
            <td class="py-4 px-6 font-mono font-semibold text-slate-700">{{ tx.part_code || tx.part_oem }}</td>
            <td class="py-4 px-6 font-medium text-slate-900">{{ tx.part_name }}</td>
            <td class="py-4 px-6 text-center">
              <span :class="['inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold',
                tx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600']">
                {{ tx.type === 'IN' ? t.txIn : t.txOut }}
              </span>
            </td>
            <td class="py-4 px-6 font-bold text-slate-800">{{ tx.quantity }}</td>
            <td class="py-4 px-6 text-slate-600">$ {{ tx.unit_price.toFixed(2) }}</td>
            <td class="py-4 px-6 font-bold text-slate-900">$ {{ tx.total_amount.toFixed(2) }}</td>
            <td class="py-4 px-6 text-slate-600 font-medium">{{ tx.customer_or_supplier }}</td>
            <td class="py-4 px-6 text-center">
              <button 
                @click="$emit('delete-tx', tx)" 
                class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-2.5 py-1 rounded-lg font-medium transition-colors whitespace-nowrap"
              >
                {{ t.btnDelete || '删除' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { Plus, FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'

defineProps({
  transactionsList: Array
})

defineEmits(['export-transactions', 'open-tx-modal', 'delete-tx'])
const { t } = useI18n()
</script>