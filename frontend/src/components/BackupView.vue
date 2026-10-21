<!-- src/components/BackupView.vue -->
<template>
  <div class="space-y-6 max-w-6xl mx-auto pb-12 relative">
    
    <!-- 🌟 模块一：系统参数与汇率配置 -->
    <div class="bg-white/80 backdrop-blur-xl p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-5">
      <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
        <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-lg shadow-sm">⚙️</div>
        <div>
          <h3 class="font-bold text-slate-800 text-base">系统参数与公司抬头配置</h3>
          <p class="text-xs text-slate-400">配置打印小票、PDF 报价单上的公司信息，以及离线环境下的 BCV 官方汇率</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 pt-1">
        <!-- 公司基础信息 -->
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5">公司全称 / 品牌名称</label>
            <input v-model="settings.company_name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 font-semibold transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5">RIF 税号 (委内瑞拉合规)</label>
            <input v-model="settings.rif" type="text" placeholder="J-31234567-8" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 font-mono transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5">门店地址 (Address)</label>
            <input v-model="settings.address" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5">公司电话 (Phone)</label>
            <input v-model="settings.phone" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-amber-500 font-mono transition-colors" />
          </div>
        </div>

        <!-- 汇率配置专区 -->
        <div class="bg-blue-50/40 p-5 rounded-2xl border border-blue-100 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="block text-sm font-black text-blue-900">💱 手动汇率配置 (BCV)</label>
              <span class="bg-blue-100 text-blue-700 px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wider uppercase">Offline Mode</span>
            </div>
            <p class="text-xs text-blue-700/80 mb-4 leading-relaxed">
              由于本系统处于离线运行状态，您必须手动设置本地的 BCV 汇率。该数值将用于所有 POS 收银结算与财务报表计算。
            </p>
            <div class="flex items-center gap-3">
              <div class="relative flex-1">
                <span class="absolute left-4 top-3 text-sm font-bold text-blue-500">Bs.</span>
                <input 
                  v-model.number="rateInput" 
                  type="number" 
                  step="0.01" 
                  class="w-full bg-white border border-blue-200 rounded-xl pl-12 pr-4 py-2.5 text-lg outline-none focus:border-blue-500 font-black font-mono text-blue-900 transition-colors" 
                />
              </div>
              <div class="text-xs font-bold text-slate-400">/ 1 USD</div>
            </div>
          </div>
          
          <div class="flex gap-2 mt-4 pt-4 border-t border-blue-100">
            <button @click="saveRate" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer">
              💾 保存当前汇率
            </button>
            <button @click="autoFetchRate" :disabled="isFetchingRate" class="bg-white hover:bg-blue-50 text-blue-600 border border-blue-200 py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer">
              <span v-if="isFetchingRate">⏳ 获取中</span>
              <span v-else>🌐 联网获取</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex justify-end pt-2 border-t border-slate-100">
        <button @click="saveSettings" class="bg-amber-600 hover:bg-amber-700 text-white px-6 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-amber-500/20 transition-all cursor-pointer flex items-center gap-2">
          💾 保存系统抬头配置
        </button>
      </div>
    </div>

    <!-- 🌟 模块二与模块三的容器 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- 左侧：数据备份区 -->
      <div class="space-y-6">
        <!-- 商品与客户备份 -->
        <div class="bg-white/80 backdrop-blur-xl p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-5">
          <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg shadow-sm">📦</div>
            <div>
              <h3 class="font-bold text-slate-800 text-base">数据导出与备份</h3>
              <p class="text-xs text-slate-400">生成商品库存与客户账本的 CSV 备份文件</p>
            </div>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button @click="$emit('export-parts')" class="bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 py-3.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer">
              <FileSpreadsheet :size="16" /> 导出商品 CSV
            </button>
            <button @click="$emit('export-clients')" class="bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 py-3.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer">
              <FileSpreadsheet :size="16" /> 导出客户 CSV
            </button>
          </div>

          <button @click="$emit('download-db')" class="w-full bg-slate-900 hover:bg-slate-800 text-white py-3.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer mt-2">
            🛡️ 下载完整数据库 (.db)
          </button>
        </div>

        <!-- 批量导入 -->
        <div class="bg-white/80 backdrop-blur-xl p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
          <div class="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg shadow-sm">📥</div>
            <div>
              <h3 class="font-bold text-slate-800 text-base">批量导入商品</h3>
              <p class="text-xs text-slate-400">通过 CSV 文件批量更新库存与进价信息</p>
            </div>
          </div>
          
          <div class="flex gap-2">
            <button @click="downloadCsvTemplate" class="flex-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer">
              📄 下载标准模板
            </button>
          </div>

          <div class="border-2 border-dashed border-slate-200 rounded-2xl p-4 text-center hover:bg-slate-50 transition-colors">
            <input 
              type="file" 
              ref="fileInputRef"
              accept=".csv" 
              @change="handleFileSelect" 
              class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer" 
            />
            <p class="text-[11px] text-slate-400 mt-2">请选择符合模板格式的 CSV 文件</p>
          </div>
          
          <button 
            v-if="selectedFile" 
            @click="uploadCsv" 
            class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl text-xs font-bold shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            🚀 确认导入 ({{ selectedFile.name }})
          </button>
        </div>
      </div>

      <!-- 右侧：系统维护 -->
      <div class="space-y-6">
        <div class="bg-white/80 backdrop-blur-xl p-6 rounded-3xl border border-rose-200/60 shadow-sm space-y-4">
          <div class="flex items-center gap-3 border-b border-rose-100 pb-4">
            <div class="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-lg shadow-sm">🧹</div>
            <div>
              <h3 class="font-bold text-rose-800 text-base">数据库清理与优化</h3>
              <p class="text-xs text-rose-500/80">执行 VACUUM 释放磁盘空间并优化查询性能</p>
            </div>
          </div>

          <div class="bg-rose-50/50 p-4 rounded-xl border border-rose-100">
            <p class="text-[11px] text-rose-700 leading-relaxed font-medium">
              ⚠️ 注意：定期执行数据库碎片整理可以有效减小文件体积、提高索引查询速度。在执行期间请勿强行关闭后端服务或断电。
            </p>
          </div>

          <button @click="showCleanupModal = true" class="w-full bg-rose-600 hover:bg-rose-700 text-white py-3.5 rounded-xl text-xs font-bold shadow-md shadow-rose-500/20 transition-all shrink-0 cursor-pointer">
            ⚡ 开始清理与优化数据库
          </button>
        </div>
      </div>

    </div>

    <!-- 🌟 通知提示浮窗 -->
    <transition name="fade">
      <div v-if="toast.show" class="fixed bottom-8 right-8 z-50 flex items-center gap-3 bg-slate-900 text-white px-5 py-3.5 rounded-2xl shadow-2xl border border-slate-800">
        <span class="text-lg">{{ toast.icon }}</span>
        <span class="text-xs font-bold">{{ toast.message }}</span>
      </div>
    </transition>

    <!-- 🌟 数据库清理确认模态框 -->
    <div v-if="showCleanupModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
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
import { apiFetch } from '../utils/api'
import { useInventory } from '../composables/useInventory'

defineEmits(['export-parts', 'export-clients', 'download-db'])
const { t } = useI18n()

// 获取汇率状态
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

// 🌟 保存手动输入的汇率
const saveRate = async () => {
  const val = parseFloat(rateInput.value)
  if (isNaN(val) || val <= 0) {
    showToast('请输入有效的汇率数字', '❌')
    return
  }
  const ok = await updateBcvRate(val)
  if (ok) {
    showToast('本地汇率已成功更新并应用！', '💱')
  } else {
    showToast('汇率保存失败', '❌')
  }
}

// 🌟 尝试联网自动获取
const autoFetchRate = async () => {
  isFetchingRate.value = true
  try {
    // 请求后端的自动抓取接口
    const res = await apiFetch('/api/bcv-rate')
    if (res.ok) {
      const data = await res.json()
      const newRate = data.rate.toFixed(2)
      rateInput.value = newRate
      
      // 🌟 核心修复：获取成功后，直接调用 updateBcvRate 保存并更新全局状态
      const ok = await updateBcvRate(newRate)
      if (ok) {
        showToast('联网获取并应用汇率成功！', '🌐')
      } else {
        showToast('获取成功，但保存失败，请手动点击保存', '❌')
      }
    } else {
      showToast('网络抓取失败，请手动输入', '❌')
    }
  } catch (e) {
    showToast('网络连接异常，请手动输入', '❌')
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
  // 初始化时，把当前的汇率带进输入框
  rateInput.value = bcvRate.value
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

  try {
    const res = await apiFetch('/api/import/parts', {
      method: 'POST',
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
  const csvContent = "oem,name,brand,category,stock,price,cost_price,bin_location\n17801-74060,空气滤清器,Toyota,滤清器,20,15.00,10.00,Estante A-1\n90915-YZZE1,机油滤清器,Toyota,滤清器,50,8.50,5.00,Estante A-2";
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