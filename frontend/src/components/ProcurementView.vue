<!-- src/components/ProcurementView.vue -->
<template>
  <div class="space-y-6">
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-4 md:p-6 space-y-6">
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 class="font-bold text-slate-900 text-base">{{ t.procurementTitle }}</h3>
          <p class="text-xs text-slate-500 mt-0.5">{{ t.procurementDesc }}</p>
        </div>
        
        <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
          <!-- 修正绑定方式 -->
          <select 
            :value="procurementBrand" 
            @change="$emit('update:procurementBrand', $event.target.value); $emit('filter-change')" 
            class="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-xl px-3 py-2 outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="ALL">{{ t.allBrands }}</option>
            <option v-for="b in uniqueBrands" :key="b" :value="b">{{ b }}</option>
          </select>

          <!-- 修正绑定方式 -->
          <select 
            :value="procurementCategory" 
            @change="$emit('update:procurementCategory', $event.target.value); $emit('filter-change')" 
            class="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-xl px-3 py-2 outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="ALL">{{ t.allCategories }}</option>
            <option v-for="c in uniqueCategories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[750px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-6">{{ t.colCode }}</th>
              <th class="py-3.5 px-6">{{ t.colOem }}</th>
              <th class="py-3.5 px-6">{{ t.colName }}</th>
              <th class="py-3.5 px-6">{{ t.colBrand }}</th>
              <th class="py-3.5 px-6">{{ t.colCategory }}</th>
              <th class="py-3.5 px-6">{{ t.colStock }}</th>
              <th class="py-3.5 px-6 text-blue-600 font-bold">{{ t.suggestedQty }}</th>
              <th class="py-3.5 px-6">{{ t.estimatedCost }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="procurementList.length === 0">
              <td colspan="8" class="text-center py-12 text-slate-400 text-xs">
                {{ t.noProcurementNeeded }}
              </td>
            </tr>
            <tr v-for="item in procurementList" :key="item.code" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-4 px-6 font-mono font-semibold text-slate-700">{{ item.code }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ item.oem }}</td>
              <td class="py-4 px-6 font-medium text-slate-900">{{ item.name }}</td>
              <td class="py-4 px-6"><span class="bg-slate-100 px-2.5 py-1 rounded-md text-xs font-medium">{{ item.brand }}</span></td>
              <td class="py-4 px-6"><span class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded text-xs font-semibold">{{ item.category }}</span></td>
              <td class="py-4 px-6 font-bold text-rose-600">{{ item.current_stock }}</td>
              <td class="py-4 px-6 font-black text-blue-600 text-base">+ {{ item.suggested_qty }}</td>
              <td class="py-4 px-6 font-bold text-emerald-600">$ {{ item.estimated_cost.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from '../composables/useI18n'

defineProps({
  procurementList: Array,
  uniqueBrands: Array,
  uniqueCategories: Array,
  procurementBrand: String,
  procurementCategory: String
})

defineEmits(['update:procurementBrand', 'update:procurementCategory', 'filter-change'])
const { t } = useI18n()
</script>