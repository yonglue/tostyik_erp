<!-- src/components/BackupView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-12 relative">
    
    <!-- ==================== 第一层：页面大标题 ==================== -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
          <span>🗄️</span> 系统运维与数据备份
        </h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">配置系统基础信息、执行自动备份策略、管理数据导入导出以及数据库底层优化。</p>
      </div>
    </div>

    <!-- ==================== 系统参数与汇率配置（全宽） ==================== -->
    <div class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl p-6 rounded-3xl border border-slate-200/80 dark:border-slate-700 shadow-sm space-y-5">
      <div class="flex items-center gap-3 border-b border-slate-100 dark:border-slate-700 pb-4">
        <div class="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center font-bold text-lg shadow-sm">⚙️</div>
        <div>
          <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base">{{ tExt.settingsTitle }}</h3>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{{ tExt.settingsSub }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-1">
        <!-- 公司基础信息 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1.5">{{ tExt.labelCompanyName }}</label>
            <input v-model="settings.company_name" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 font-semibold transition-colors dark:text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1.5">{{ tExt.labelRif }}</label>
            <input v-model="settings.rif" type="text" placeholder="J-31234567-8" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 font-mono transition-colors dark:text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1.5">{{ tExt.labelPhone }}</label>
            <input v-model="settings.phone" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 font-mono transition-colors dark:text-white" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1.5">{{ tExt.labelAddress }}</label>
            <input v-model="settings.address" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 transition-colors dark:text-white" />
          </div>
        </div>

        <!-- 汇率配置专区 -->
        <div class="bg-blue-50/40 dark:bg-blue-900/20 p-5 rounded-2xl border border-blue-100 dark:border-blue-800/50 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="block text-sm font-black text-blue-900 dark:text-blue-300">{{ tExt.rateTitle }}</label>
              <span class="bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300 px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wider uppercase">{{ tExt.offlineMode }}</span>
            </div>
            <p class="text-xs text-blue-700/80 dark:text-blue-400/80 mb-4 leading-relaxed">
              {{ tExt.rateDesc }}
            </p>
            <div class="flex items-center gap-3">
              <div class="relative flex-1">
                <span class="absolute left-4 top-3 text-sm font-bold text-blue-500">Bs.</span>
                <input 
                  v-model.number="rateInput" 
                  type="number" 
                  step="0.01" 
                  class="w-full bg-white dark:bg-slate-900 border border-blue-200 dark:border-blue-700 rounded-xl pl-12 pr-4 py-2.5 text-lg outline-none focus:border-blue-500 font-black font-mono text-blue-900 dark:text-blue-300 transition-colors" 
                />
              </div>
              <div class="text-xs font-bold text-slate-400 dark:text-slate-500">/ 1 USD</div>
            </div>
          </div>
          
          <div class="flex gap-2 mt-4 pt-4 border-t border-blue-100 dark:border-blue-800/50">
            <button @click="saveRate" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer">
              💾 {{ tExt.btnSaveRate }}
            </button>
            <button @click="autoFetchRate" :disabled="isFetchingRate" class="bg-white dark:bg-slate-800 hover:bg-blue-50 dark:hover:bg-slate-700 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-700 py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer">
              <span v-if="isFetchingRate">⏳ {{ tExt.fetching }}</span>
              <span v-else>🌐 {{ tExt.btnFetchOnline }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex justify-end pt-2 border-t border-slate-100 dark:border-slate-700">
        <button @click="saveSettings" class="bg-amber-600 hover:bg-amber-700 text-white px-6 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-amber-500/20 transition-all cursor-pointer flex items-center gap-2">
          💾 {{ tExt.btnSaveSettings }}
        </button>
      </div>
    </div>

    <!-- ==================== 2x2 网格：数据维护区 ==================== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- 模块 1：自动备份系统 -->
      <div class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl p-6 rounded-3xl border border-slate-200/80 dark:border-slate-700 shadow-sm space-y-5">
        <div class="flex items-center gap-3 border-b border-slate-100 dark:border-slate-700 pb-4">
          <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-lg shadow-sm">🛡️</div>
          <div>
            <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base">自动备份系统</h3>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">系统每 24 小时自动备份一次，防止数据丢失</p>
          </div>
        </div>
        
        <div class="flex justify-between items-center">
          <p class="text-xs text-slate-500 dark:text-slate-400">目前保留最近 30 天的备份文件</p>
          <button @click="triggerBackup" :disabled="isBackingUp" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer disabled:opacity-50">
            {{ isBackingUp ? '备份中...' : '手动立即备份' }}
          </button>
        </div>

        <div class="space-y-2 max-h-48 overflow-y-auto custom-scrollbar pr-2">
          <div v-for="bf in backupList" :key="bf.filename" class="flex items-center justify-between bg-slate-50 dark:bg-slate-900 p-3 rounded-xl border border-slate-100 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <div>
              <p class="font-mono text-xs font-bold text-slate-800 dark:text-slate-200">{{ bf.filename }}</p>
              <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-1">{{ bf.created_at }} | {{ bf.size_mb }} MB</p>
            </div>
            <button @click="downloadBackup(bf.filename)" class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 font-bold px-2 py-1 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 rounded-lg transition-colors cursor-pointer">
              📥 下载
            </button>
          </div>
          <div v-if="backupList.length === 0" class="text-center py-6 text-slate-400 text-xs">
            暂无备份记录
          </div>
        </div>
      </div>

      <!-- 模块 2：数据导出与备份 -->
      <div class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl p-6 rounded-3xl border border-slate-200/80 dark:border-slate-700 shadow-sm space-y-5">
        <div class="flex items-center gap-3 border-b border-slate-100 dark:border-slate-700 pb-4">
          <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-lg shadow-sm">📦</div>
          <div>
            <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base">{{ tExt.exportTitle }}</h3>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{{ tExt.exportSub }}</p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button @click="$emit('export-parts')" class="bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 py-3.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer">
            <FileSpreadsheet :size="16" /> {{ tExt.btnExportParts }}
          </button>
          <button @click="$emit('export-clients')" class="bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 py-3.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer">
            <FileSpreadsheet :size="16" /> {{ tExt.btnExportClients }}
          </button>
        </div>

        <button @click="$emit('download-db')" class="w-full bg-slate-900 hover:bg-slate-800 dark:bg-slate-700 dark:hover:bg-slate-600 text-white py-3.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer mt-2">
          🛡️ {{ tExt.btnDownloadDb }}
        </button>
      </div>

      <!-- 模块 3：批量导入商品 -->
      <div class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl p-6 rounded-3xl border border-slate-200/80 dark:border-slate-700 shadow-sm space-y-4">
        <div class="flex items-center gap-3 border-b border-slate-100 dark:border-slate-700 pb-4">
          <div class="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-lg shadow-sm">📥</div>
          <div>
            <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base">{{ tExt.importTitle }}</h3>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{{ tExt.importSub }}</p>
          </div>
        </div>
        
        <div class="flex gap-2">
          <button @click="downloadTemplate" class="flex-1 bg-emerald-50 dark:bg-emerald-900/30 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer">
            📄 {{ tExt.btnDownloadTemplate }}
          </button>
        </div>

        <div class="border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-2xl p-4 text-center hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
          <input 
            type="file" 
            ref="fileInputRef"
            accept=".csv, .xlsx, .xls" 
            @change="handleFileSelect" 
            class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 dark:file:bg-slate-700 file:text-blue-700 dark:file:text-blue-300 hover:file:bg-blue-100 cursor-pointer" 
          />
          <p class="text-[11px] text-slate-400 dark:text-slate-500 mt-2">{{ tExt.fileHint }}</p>
        </div>
        
        <button 
          v-if="selectedFile" 
          @click="uploadCsv" 
          class="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl text-xs font-bold shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer mt-2"
        >
          🚀 {{ tExt.btnConfirmImport }} ({{ selectedFile.name }})
        </button>
      </div>

      <!-- 模块 4：数据库清理与优化 -->
      <div class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl p-6 rounded-3xl border border-rose-200/60 dark:border-rose-900/50 shadow-sm space-y-4">
        <div class="flex items-center gap-3 border-b border-rose-100 dark:border-rose-900/50 pb-4">
          <div class="w-10 h-10 rounded-xl bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center justify-center font-bold text-lg shadow-sm">🧹</div>
          <div>
            <h3 class="font-bold text-rose-800 dark:text-rose-300 text-base">{{ tExt.cleanupTitle }}</h3>
            <p class="text-xs text-rose-500/80 dark:text-rose-400/80 mt-0.5">{{ tExt.cleanupSub }}</p>
          </div>
        </div>

        <div class="bg-rose-50/50 dark:bg-rose-900/20 p-4 rounded-xl border border-rose-100 dark:border-rose-900/50 flex-1">
          <p class="text-[11px] text-rose-700 dark:text-rose-300 leading-relaxed font-medium">
            {{ tExt.cleanupWarning }}
          </p>
        </div>

        <button @click="showCleanupModal = true" class="w-full bg-rose-600 hover:bg-rose-700 text-white py-3.5 rounded-xl text-xs font-bold shadow-md shadow-rose-500/20 transition-all shrink-0 cursor-pointer mt-auto">
          ⚡ {{ tExt.btnCleanup }}
        </button>
      </div>

    </div>

    <!-- 🌟 通知提示浮窗 -->
    <transition name="fade">
      <div v-if="toast.show" class="fixed bottom-8 right-8 z-50 flex items-center gap-3 bg-slate-900 dark:bg-slate-700 text-white px-5 py-3.5 rounded-2xl shadow-2xl border border-slate-800 dark:border-slate-600">
        <span class="text-lg">{{ toast.icon }}</span>
        <span class="text-xs font-bold">{{ toast.message }}</span>
      </div>
    </transition>

    <!-- 🌟 统一确认弹窗 -->
    <ConfirmDialog
      :visible="showCleanupModal"
      overlay-class="bg-slate-900/60"
      :title="tExt.confirmCleanupTitle"
      :message="tExt.confirmCleanupMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="tExt.btnCleanup"
      @cancel="showCleanupModal = false"
      @confirm="runCleanup"
    />

    <!-- 🌟 导入进度遮罩 -->
    <div v-if="isImporting" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex flex-col items-center justify-center">
      <div class="bg-white dark:bg-slate-800 p-8 rounded-3xl shadow-2xl w-96 text-center space-y-4">
        <div class="text-4xl animate-bounce">📥</div>
        <h3 class="font-bold text-lg dark:text-white">正在上传并解析数据</h3>
        <div class="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-4 overflow-hidden">
          <div class="bg-indigo-600 h-4 rounded-full transition-all duration-300" :style="{ width: importProgress + '%' }"></div>
        </div>
        <p class="text-sm text-slate-500 dark:text-slate-400">{{ importProgress }}% 已上传</p>
      </div>
    </div>

    <!-- 🌟 导入结果报告弹窗 -->
    <div v-if="showImportReport" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-800 p-6 rounded-3xl shadow-2xl max-w-lg w-full space-y-4">
        <h3 class="font-bold text-lg dark:text-white flex items-center gap-2">
          <span>{{ importStats.imported > 0 ? '✅' : '❌' }}</span> 导入结果报告
        </h3>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-emerald-50 dark:bg-emerald-900/20 p-4 rounded-xl text-center">
            <p class="text-xs text-emerald-600 font-bold">成功导入</p>
            <p class="text-2xl font-black text-emerald-700 dark:text-emerald-400">{{ importStats.imported }}</p>
          </div>
          <div class="bg-rose-50 dark:bg-rose-900/20 p-4 rounded-xl text-center">
            <p class="text-xs text-rose-600 font-bold">跳过 / 失败</p>
            <p class="text-2xl font-black text-rose-700 dark:text-rose-400">{{ importStats.skipped }}</p>
          </div>
        </div>

        <div v-if="importErrorDetails.length > 0" class="space-y-2">
          <p class="text-xs font-bold text-slate-500">错误明细（最多显示前 5 条）:</p>
          <ul class="text-xs text-rose-500 bg-rose-50 dark:bg-rose-900/20 p-3 rounded-xl max-h-32 overflow-y-auto">
            <li v-for="(err, i) in importErrorDetails" :key="i" class="mb-1">{{ err }}</li>
          </ul>
        </div>

        <button @click="closeImportReport" class="w-full bg-slate-900 hover:bg-slate-800 dark:bg-slate-700 dark:hover:bg-slate-600 text-white py-3 rounded-xl font-bold transition-all cursor-pointer">
          知道了
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiFetch, apiUrl } from '../utils/api'
import { useInventory } from '../composables/useInventory'
import ConfirmDialog from './ConfirmDialog.vue'

defineEmits(['export-parts', 'export-clients', 'download-db'])
const { t, currentLang } = useI18n()

const { bcvRate, updateBcvRate } = useInventory()
const rateInput = ref(36.50)
const isFetchingRate = ref(false)

const settings = ref({
  company_name: '',
  rif: '',
  address: '',
  phone: '',
  email: ''
})

const showCleanupModal = ref(false)

const backupList = ref([])
const isBackingUp = ref(false)

const fetchBackups = async () => {
  try {
    const res = await apiFetch('/api/backup/list')
    if (res.ok) {
      backupList.value = await res.json()
    }
  } catch (e) { console.error(e) }
}

const triggerBackup = async () => {
  isBackingUp.value = true
  try {
    const res = await apiFetch('/api/backup/trigger', { method: 'POST' })
    if (res.ok) {
      showToast('✅ 备份成功！', '🎉')
      await fetchBackups()
    } else {
      showToast('❌ 备份失败，请检查数据库', '❌')
    }
  } catch (e) {
    showToast('❌ 网络异常', '❌')
  } finally {
    isBackingUp.value = false
  }
}

const downloadBackup = (filename) => {
  window.open(apiUrl(`/api/backup/download/${filename}`), '_blank')
}

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    settingsTitle: isZh ? '系统参数与公司抬头配置' : isEs ? 'Configuración de Empresa' : 'Company Settings',
    settingsSub: isZh ? '配置打印小票、PDF 报价单上的公司信息，以及离线环境下的 BCV 官方汇率' : isEs ? 'Configure la información en PDF y la tasa BCV' : 'Configure company info and BCV rate',
    labelCompanyName: isZh ? '公司全称 / 品牌名称' : isEs ? 'Nombre de la Empresa' : 'Company Name',
    labelRif: isZh ? 'RIF 税号 (委内瑞拉合规)' : isEs ? 'RIF (Cumplimiento)' : 'RIF Tax ID',
    labelAddress: isZh ? '门店地址 (Address)' : isEs ? 'Dirección' : 'Address',
    labelPhone: isZh ? '公司电话 (Phone)' : isEs ? 'Teléfono' : 'Phone',
    
    rateTitle: isZh ? '手动汇率配置 (BCV)' : isEs ? 'Configuración de Tasa BCV' : 'Manual BCV Rate',
    offlineMode: isZh ? '离线模式' : isEs ? 'Modo Offline' : 'Offline Mode',
    rateDesc: isZh ? '由于本系统处于离线运行状态，您必须手动设置本地的 BCV 汇率。该数值将用于所有 POS 收银结算与财务报表计算。' : isEs ? 'Configure la tasa local de BCV. Se usará para todas las ventas y finanzas.' : 'Set local BCV rate. Used for all POS and finance calculations.',
    btnSaveRate: isZh ? '保存当前汇率' : isEs ? 'Guardar Tasa' : 'Save Rate',
    fetching: isZh ? '获取中' : isEs ? 'Obteniendo' : 'Fetching',
    btnFetchOnline: isZh ? '联网获取' : isEs ? 'Obtener Online' : 'Fetch Online',
    btnSaveSettings: isZh ? '保存系统抬头配置' : isEs ? 'Guardar Configuración' : 'Save Settings',
    
    exportTitle: isZh ? '数据导出与备份' : isEs ? 'Exportación y Respaldo' : 'Data Export & Backup',
    exportSub: isZh ? '生成商品库存与客户账本的 CSV 备份文件' : isEs ? 'Generar archivos CSV de inventario y clientes' : 'Generate CSV backups for parts and clients',
    btnExportParts: isZh ? '导出商品 CSV' : isEs ? 'Exportar Repuestos' : 'Export Parts',
    btnExportClients: isZh ? '导出客户 CSV' : isEs ? 'Exportar Clientes' : 'Export Clients',
    btnDownloadDb: isZh ? '下载完整数据库 (.db)' : isEs ? 'Descargar Base de Datos' : 'Download Database',
    
    importTitle: isZh ? '批量导入商品' : isEs ? 'Importar Repuestos' : 'Import Parts',
    importSub: isZh ? '通过 Excel/CSV 文件批量更新库存与进价信息' : isEs ? 'Actualice inventario y costos mediante Excel/CSV' : 'Update inventory and cost via Excel/CSV',
    btnDownloadTemplate: isZh ? '下载高级 Excel 模板' : isEs ? 'Descargar Plantilla Excel' : 'Download Excel Template',
    fileHint: isZh ? '请选择符合模板格式的 Excel 或 CSV 文件' : isEs ? 'Seleccione un archivo Excel o CSV válido' : 'Select a valid Excel or CSV file',
    btnConfirmImport: isZh ? '确认导入' : isEs ? 'Confirmar Importación' : 'Confirm Import',
    
    cleanupTitle: isZh ? '数据库清理与优化' : isEs ? 'Limpieza de Base de Datos' : 'Database Cleanup',
    cleanupSub: isZh ? '执行 VACUUM 释放磁盘空间并优化查询性能' : isEs ? 'Ejecute VACUUM para liberar espacio y optimizar' : 'Run VACUUM to free space and optimize',
    cleanupWarning: isZh ? '⚠️ 注意：定期执行数据库碎片整理可以有效减小文件体积、提高索引查询速度。在执行期间请勿强行关闭后端服务或断电。' : isEs ? '⚠️ Nota: La limpieza optimiza el archivo. No cierre el servidor durante el proceso.' : '⚠️ Note: Cleanup optimizes the file. Do not close the server during the process.',
    btnCleanup: isZh ? '开始清理与优化数据库' : isEs ? 'Iniciar Limpieza' : 'Start Cleanup',
    confirmCleanupTitle: isZh ? '确认执行数据库优化' : isEs ? 'Confirmar Limpieza' : 'Confirm Cleanup',
    confirmCleanupMsg: isZh ? '此操作将释放 SQLite 未使用的磁盘空间并整理内存碎片。在执行期间请勿强行关闭服务或断电。' : isEs ? 'Esta acción liberará espacio en disco. No cierre el servicio.' : 'This action will free disk space. Do not close the service.',
    
    toastSettingsSaved: isZh ? '系统抬头与参数配置已成功保存！' : isEs ? '¡Configuración guardada!' : 'Settings saved successfully!',
    toastSettingsFail: isZh ? '保存配置失败' : isEs ? 'Error al guardar' : 'Failed to save',
    toastRateInvalid: isZh ? '请输入有效的汇率数字' : isEs ? 'Ingrese una tasa válida' : 'Enter a valid rate',
    toastRateSaved: isZh ? '本地汇率已成功更新并应用！' : isEs ? '¡Tasa local actualizada!' : 'Local rate updated and applied!',
    toastRateFail: isZh ? '汇率保存失败' : isEs ? 'Error al guardar la tasa' : 'Failed to save rate',
    toastFetchSuccess: isZh ? '联网获取并应用汇率成功！' : isEs ? '¡Tasa obtenida y aplicada!' : 'Rate fetched and applied successfully!',
    toastFetchFail: isZh ? '网络抓取失败，请手动输入' : isEs ? 'Error al obtener, ingrese manualmente' : 'Fetch failed, enter manually',
    toastNetworkError: isZh ? '网络连接异常' : isEs ? 'Error de conexión' : 'Network error',
    toastCleanupSuccess: isZh ? '数据库清理与空间优化已成功完成！' : isEs ? '¡Limpieza completada!' : 'Cleanup and optimization completed!',
    toastCleanupFail: isZh ? '数据库清理执行失败' : isEs ? 'Error en la limpieza' : 'Cleanup failed',
    toastImportSuccess: isZh ? '批量导入成功！共处理/更新了' : isEs ? '¡Importación exitosa! Procesados:' : 'Import successful! Processed:',
    toastImportFail: isZh ? '导入失败，请检查文件编码或格式。' : isEs ? 'Error de importación, revise el archivo.' : 'Import failed, check file format.'
  }
})

const toast = reactive({
  show: false,
  message: '',
  icon: '🎉'
})

const showToast = (msg, icon = '🎉') => {
  toast.message = msg
  toast.icon = icon
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

watch(bcvRate, (newVal) => {
  if (newVal) rateInput.value = newVal
}, { immediate: true })

const fetchSettings = async () => {
  try {
    const res = await apiFetch('/api/settings')
    if (res.ok) {
      settings.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

const saveSettings = async () => {
  try {
    const res = await apiFetch('/api/settings', {
      method: 'POST',
      body: JSON.stringify(settings.value)
    })
    if (res.ok) {
      showToast(tExt.value.toastSettingsSaved, '🎉')
    } else {
      const errData = await res.json().catch(() => ({}))
      showToast(`${tExt.value.toastSettingsFail}: ${errData.detail || res.statusText}`, '❌')
    }
  } catch (e) {
    console.error(e)
    showToast(tExt.value.toastNetworkError, '❌')
  }
}

const saveRate = async () => {
  const val = parseFloat(rateInput.value)
  if (isNaN(val) || val <= 0) {
    showToast(tExt.value.toastRateInvalid, '❌')
    return
  }
  const ok = await updateBcvRate(val)
  if (ok) {
    showToast(tExt.value.toastRateSaved, '💱')
  } else {
    showToast(tExt.value.toastRateFail, '❌')
  }
}

const autoFetchRate = async () => {
  isFetchingRate.value = true
  try {
    const res = await apiFetch('/api/bcv-rate')
    if (res.ok) {
      const data = await res.json()
      const newRate = data.rate.toFixed(2)
      rateInput.value = newRate
      
      const ok = await updateBcvRate(newRate)
      if (ok) {
        showToast(tExt.value.toastFetchSuccess, '🌐')
      } else {
        showToast(tExt.value.toastRateFail, '❌')
      }
    } else {
      showToast(tExt.value.toastFetchFail, '❌')
    }
  } catch (e) {
    showToast(tExt.value.toastNetworkError, '❌')
  } finally {
    isFetchingRate.value = false
  }
}

const runCleanup = async () => {
  showCleanupModal.value = false
  try {
    const res = await apiFetch('/api/settings/cleanup', {
      method: 'POST'
    })
    if (res.ok) {
      const data = await res.json()
      showToast(data.message || tExt.value.toastCleanupSuccess, '⚡')
    } else {
      showToast(tExt.value.toastCleanupFail, '❌')
    }
  } catch (e) {
    console.error(e)
    showToast(tExt.value.toastNetworkError, '❌')
  }
}

onMounted(() => {
  fetchSettings()
  fetchBackups()
})

const selectedFile = ref(null)
const fileInputRef = ref(null)

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const uploadCsv = () => {
  if (!selectedFile.value) return
  
  isImporting.value = true
  importProgress.value = 0
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  const xhr = new XMLHttpRequest()
  xhr.open('POST', apiUrl('/api/import/parts'), true)
  
  const token = localStorage.getItem('tostiyk_token')
  if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)

  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      importProgress.value = Math.round((e.loaded / e.total) * 100)
    }
  }

  xhr.onload = () => {
    isImporting.value = false
    
    if (xhr.status >= 200 && xhr.status < 300) {
      const data = JSON.parse(xhr.responseText)
      
      importStats.value = {
        imported: data.imported_count,
        skipped: data.skipped_count
      }
      importErrorDetails.value = data.errors || []
      showImportReport.value = true

      if (data.imported_count > 0) {
        selectedFile.value = null
        if (fileInputRef.value) fileInputRef.value.value = ''
      }
    } else {
      try {
        const data = JSON.parse(xhr.responseText)
        showToast(`❌ 导入失败: ${data.detail}`, '❌')
      } catch (e) {
        showToast('❌ 导入失败: 服务器返回了未知错误', '❌')
      }
    }
  }

  xhr.onerror = () => {
    isImporting.value = false
    showToast('❌ 网络连接异常', '❌')
  }

  xhr.send(formData)
}

const isImporting = ref(false)
const importProgress = ref(0)
const showImportReport = ref(false)
const importStats = ref({ imported: 0, skipped: 0 })
const importErrorDetails = ref([])

const closeImportReport = () => {
  showImportReport.value = false
}

const downloadTemplate = () => {
  window.open(apiUrl('/api/export/template/parts'), '_blank')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>