<!-- src/components/BackupView.vue -->
<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-12 relative">
    
    <!-- 🌟 模块一：系统参数与公司抬头配置 (RIF / 地址 / 电话) -->
    <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-5">
      <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
        <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-lg">🏢</div>
        <div>
          <h3 class="font-bold text-slate-800 text-base">系统参数与公司抬头配置</h3>
          <p class="text-xs text-slate-400">配置打印小票及 PDF 报价单上的公司名称、RIF税号、地址与联系方式</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1.5">公司全称 / 品牌名称</label>
          <input v-model="settings.company_name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-semibold" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1.5">RIF 税号 (委内瑞拉合规)</label>
          <input v-model="settings.rif" type="text" placeholder="J-31234567-8" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1.5">门店地址 (Address)</label>
          <input v-model="settings.address" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1.5">公司电话 (Phone)</label>
          <input v-model="settings.phone" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" />
        </div>
      </div>

      <div class="flex justify-end pt-2">
        <button @click="saveSettings" class="bg-amber-600 hover:bg-amber-700 text-white px-6 py-2.5 rounded-xl text-xs font-bold shadow-md transition-all cursor-pointer">
          💾 保存抬头与参数配置
        </button>
      </div>
    </div>

    <!-- 🌟 模块二：数据清理与一键归档 -->
    <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
      <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
        <div class="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-lg">🧹</div>
        <div>
          <h3 class="font-bold text-slate-800 text-base">数据清理与一键归档</h3>
          <p class="text-xs text-slate-400">执行 SQLite 数据库空间碎片整理（VACUUM），优化系统运行性能</p>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <div class="text-xs text-slate-500">
          定期执行数据库碎片整理可以有效减小文件体积、提高索引查询速度，确保系统在高并发收银时保持丝滑流畅。
        </div>
        <button @click="showCleanupModal = true" class="w-full sm:w-auto bg-rose-600 hover:bg-rose-700 text-white px-6 py-3 rounded-xl text-xs font-bold shadow-md transition-all shrink-0 cursor-pointer">
          ⚡ 开始清理与优化数据库
        </button>
      </div>
    </div>

    <!-- 🌟 模块三：商品与客户备份、数据库下载 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- 商品库存备份与导入 -->
      <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
        <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
          <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg">📦</div>
          <div>
            <h3 class="font-bold text-slate-800 text-base">{{ t.backupPartsTitle || '商品库存与 OEM 备份' }}</h3>
            <p class="text-xs text-slate-400">{{ t.backupPartsDesc || '导出商品表格或通过 CSV 批量导入更新库存' }}</p>
          </div>
        </div>
        <div class="space-y-3 pt-2">
          <button @click="$emit('export-parts')" class="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 py-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer">
            <FileSpreadsheet :size="16" /> {{ t.exportPartsBtn || '导出全部商品 CSV' }}
          </button>
          
          <button @click="downloadCsvTemplate" class="w-full bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer">
            📥 下载标准商品 CSV 模板
          </button>

          <div class="space-y-2 pt-2 border-t border-slate-100">
            <label class="block text-xs font-semibold text-slate-500">{{ t.importPartsLabel || '批量导入 CSV 商品库' }}</label>
            <input 
              type="file" 
              ref="fileInputRef"
              accept=".csv" 
              @change="handleFileSelect" 
              class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-200 rounded-xl p-2" 
            />
            
            <button 
              v-if="selectedFile" 
              @click="uploadCsv" 
              class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl text-xs font-bold shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              🚀 确认上传并导入档案 ({{ selectedFile.name }})
            </button>
          </div>
        </div>
      </div>

      <!-- 客户账本与完整数据库备份 -->
      <div class="space-y-6">
        <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg">👥</div>
            <div>
              <h3 class="font-bold text-slate-800 text-base">{{ t.backupClientsTitle || '客户档案与欠款备份' }}</h3>
              <p class="text-xs text-slate-400">导出客户名单, 电话及当前 Fiado 赊账欠款记录</p>
            </div>
          </div>
          <div class="space-y-3 pt-2">
            <button @click="$emit('export-clients')" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer">
              <FileSpreadsheet :size="16" /> {{ t.exportClientsBtn || '导出客户与欠款 CSV' }}
            </button>
          </div>
        </div>

        <div class="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div class="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-lg">🛡️</div>
            <div>
              <h3 class="font-bold text-slate-800 text-base">{{ t.backupDbTitle || '完整数据库备份' }}</h3>
              <p class="text-xs text-slate-400">一键下载 SQLite 完整底层数据库文件 (.db)</p>
            </div>
          </div>
          <div class="pt-2">
            <button @click="$emit('download-db')" class="w-full bg-slate-900 hover:bg-slate-800 text-white py-3.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer">
              📦 下载完整数据库备份 (.db)
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- 🌟 现代化自定义通知提示浮窗 -->
    <transition name="fade">
      <div v-if="toast.show" class="fixed bottom-8 right-8 z-50 flex items-center gap-3 bg-slate-900 text-white px-5 py-3.5 rounded-2xl shadow-2xl border border-slate-800">
        <span class="text-lg">{{ toast.icon }}</span>
        <span class="text-xs font-medium">{{ toast.message }}</span>
      </div>
    </transition>

    <!-- 🌟 数据库清理确认模态框 -->
    <div v-if="showCleanupModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-xl shrink-0">⚡</div>
          <div>
            <h3 class="font-bold text-slate-800 text-base">确认执行数据库优化</h3>
            <p class="text-xs text-slate-400">Database VACUUM & Space Optimization</p>
          </div>
        </div>
        <p class="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
          此操作将释放 SQLite 未使用的磁盘空间并整理内存碎片。在执行期间请勿强行关闭服务或断电。
        </p>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="showCleanupModal = false" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            取消
          </button>
          <button @click="runCleanup" class="px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-md transition-all cursor-pointer">
            确认执行
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiUrl } from '../utils/api'

defineEmits(['export-parts', 'export-clients', 'download-db'])
const { t } = useI18n()

const settings = ref({
  company_name: '',
  rif: '',
  address: '',
  phone: '',
  email: ''
})

const showCleanupModal = ref(false)

// 统一的通知浮窗状态
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

// 获取带 Token 的请求头
const getAuthHeaders = () => {
  const headers = { 'Content-Type': 'application/json' }
  try {
    const userStr = localStorage.getItem('tostiyk_current_user')
    if (userStr) {
      const user = JSON.parse(userStr)
      if (user.token) {
        headers['Authorization'] = `Bearer ${user.token}`
      }
    }
  } catch (e) {
    console.error(e)
  }
  return headers
}

const fetchSettings = async () => {
  try {
    const res = await fetch(apiUrl('/api/settings'), {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      settings.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

const saveSettings = async () => {
  try {
    const res = await fetch(apiUrl('/api/settings'), {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(settings.value)
    })
    if (res.ok) {
      showToast('系统抬头与参数配置已成功保存！', '🎉')
    } else {
      const errData = await res.json().catch(() => ({}))
      showToast(`保存配置失败: ${errData.detail || res.statusText}`, '❌')
    }
  } catch (e) {
    console.error(e)
    showToast('网络异常，无法连接后端服务', '❌')
  }
}

const runCleanup = async () => {
  showCleanupModal.value = false
  try {
    const res = await fetch(apiUrl('/api/settings/cleanup'), {
      method: 'POST',
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      showToast(data.message || '数据库清理与空间优化已成功完成！', '⚡')
    } else {
      showToast('数据库清理执行失败', '❌')
    }
  } catch (e) {
    console.error(e)
    showToast('网络或后端服务异常', '❌')
  }
}

onMounted(() => {
  fetchSettings()
})

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

  const headers = {}
  try {
    const userStr = localStorage.getItem('tostiyk_current_user')
    if (userStr) {
      const user = JSON.parse(userStr)
      if (user.token) {
        headers['Authorization'] = `Bearer ${user.token}`
      }
    }
  } catch (e) {}

  try {
    const res = await fetch(apiUrl('/api/import/parts'), {
      method: 'POST',
      headers,
      body: formData
    })
    if (res.ok) {
      const data = await res.json()
      showToast(`批量导入成功！共处理/更新了 ${data.imported_count || 0} 个 SKU 档案。`, '📦')
      selectedFile.value = null
      if (fileInputRef.value) fileInputRef.value.value = ''
    } else {
      showToast('导入失败，请检查 CSV 文件编码或格式。', '❌')
    }
  } catch (e) {
    console.error(e)
    showToast('网络或后端服务异常', '❌')
  }
}

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