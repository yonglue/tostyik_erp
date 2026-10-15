<!-- src/components/WarehouseView.vue -->
<template>
  <div class="space-y-6">
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
      <div>
        <h3 class="font-bold text-slate-800 flex items-center gap-2 text-base">
          📦 {{ t.warehouseTitle || '仓库货架与库位对照 (Bin Location Management)' }}
        </h3>
        <p class="text-xs text-slate-400 mt-1">
          {{ t.warehouseSubtitle || '精准定位每个配件在实体仓库中的货架位置（例如: Estante A-1, B-3）' }}
        </p>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3 px-4">{{ t.colPartCode || '配件编码' }}</th>
              <th class="py-3 px-4">{{ t.colOem || 'OEM 号' }}</th>
              <th class="py-3 px-4">{{ t.colPartName || '配件名称' }}</th>
              <th class="py-3 px-4">{{ t.colBrand || '适配品牌' }}</th>
              <th class="py-3 px-4">{{ t.colTotalStock || '总库存' }}</th>
              <th class="py-3 px-4">{{ t.colBinLocation || '货架库位 (BIN LOCATION)' }}</th>
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
                  <span class="text-[10px] text-emerald-600 font-normal">({{ t.defaultBinTag || '默认主货架' }})</span>
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
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'

const props = defineProps({
  partsList: {
    type: Array,
    default: () => []
  }
})

const { t } = useI18n()
</script>