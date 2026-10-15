<!-- src/components/BackupView.vue -->
<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
          <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg">📦</div>
          <div>
            <h3 class="font-bold text-slate-800 text-base">{{ t.backupPartsTitle }}</h3>
            <p class="text-xs text-slate-400">{{ t.backupPartsDesc }}</p>
          </div>
        </div>
        <div class="space-y-3 pt-2">
          <!-- 导出按钮 -->
          <button @click="$emit('export-parts')" class="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 py-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all">
            <FileSpreadsheet :size="16" /> {{ t.exportPartsBtn }}
          </button>
          
          <!-- 下载标准 CSV 模板按钮 -->
          <button @click="downloadCsvTemplate" class="w-full bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all">
            📥 下载标准商品 CSV 模板
          </button>

          <!-- 批量导入区 -->
          <div class="space-y-2 pt-2 border-t border-slate-100">
            <label class="block text-xs font-semibold text-slate-500">{{ t.importPartsLabel }}</label>
            <input 
              type="file" 
              ref="fileInputRef"
              accept=".csv" 
              @change="handleFileSelect" 
              class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-200 rounded-xl p-2" 
            />
            
            <!-- 确认上传按钮 -->
            <button 
              v-if="selectedFile" 
              @click="uploadCsv" 
              class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl text-xs font-bold shadow-md transition-all flex items-center justify-center gap-2"
            >
              🚀 确认上传并导入档案 ({{ selectedFile.name }})
            </button>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
          <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg">👥</div>
          <div>
            <h3 class="font-bold text-slate-800 text-base">{{ t.backupClientsTitle }}</h3>
            <p class="text-xs text-slate-400">{{ t.backupClientsDesc }}</p>
          </div>
        </div>
        <div class="space-y-3 pt-2">
          <button @click="$emit('export-clients')" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 shadow-md transition-all">
            <FileSpreadsheet :size="16" /> {{ t.exportClientsBtn }}
          </button>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4 md:col-span-2">
        <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
          <div class="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-lg">🛡️</div>
          <div>
            <h3 class="font-bold text-slate-800 text-base">{{ t.backupDbTitle }}</h3>
            <p class="text-xs text-slate-400">{{ t.backupDbDesc }}</p>
          </div>
        </div>
        <div class="flex gap-4 pt-2">
          <button @click="$emit('download-db')" class="bg-slate-900 hover:bg-slate-800 text-white px-6 py-3 rounded-xl text-xs font-semibold flex items-center gap-2 shadow-md transition-all">
            {{ t.downloadDbBtn }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiUrl } from '../utils/api'

defineEmits(['export-parts', 'export-clients', 'download-db'])
const { t } = useI18n()

const selectedFile = ref(null)
const fileInputRef = ref(null)

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const uploadCsv = async () => {
  if (!selectedFile.value) return
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await fetch(apiUrl('/api/import/parts'), { method: 'POST', body: formData })
    if (res.ok) {
      const data = await res.json()
      alert(`🎉 批量导入成功！共处理/更新了 ${data.imported_count} 个 SKU 档案。`)
      selectedFile.value = null
      if (fileInputRef.value) fileInputRef.value.value = ''
    } else {
      alert('❌ 导入失败，请检查 CSV 文件编码或格式。')
    }
  } catch (e) {
    console.error(e)
    alert('❌ 网络或后端服务异常')
  }
}

// 下载精简后的标准 OEM 导向 CSV 模板
const downloadCsvTemplate = () => {
  const csvContent = "oem,name,brand,category,stock,price,bin_location\n17801-74060,空气滤清器,Toyota,滤清器,20,15.00,Estante A-1\n90915-YZZE1,机油滤清器,Toyota,滤清器,50,8.50,Estante A-2";
  const blob = new Blob(["\ufeff" + csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "tostiyk_oem_parts_template.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

</script>