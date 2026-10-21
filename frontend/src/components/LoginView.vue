<!-- src/components/LoginView.vue -->
<template>
  <!-- 安全登录遮罩层 -->
  <div class="fixed inset-0 bg-slate-900 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 p-8 space-y-6 relative">

      <!-- 右上角语言切换器 -->
      <div class="absolute top-6 right-6">
        <select v-model="currentLang" class="bg-slate-100 border border-slate-200 text-xs rounded-lg px-2.5 py-1.5 outline-none font-semibold text-slate-700 cursor-pointer focus:border-blue-500 transition-colors">
          <option value="es">🇪🇸 ES</option>
          <option value="zh">🇨🇳 中文</option>
          <option value="en">🇺🇸 EN</option>
        </select>
      </div>

      <div class="text-center space-y-2 pt-2">
        <div class="w-14 h-14 rounded-2xl bg-blue-600 mx-auto flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
          <Cpu :size="28" />
        </div>
        <h2 class="font-black text-xl text-slate-900 tracking-tight">TOSTIKYK ERP</h2>
        <p class="text-xs text-slate-500 font-medium">{{ tExt.subtitle }}</p>
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ tExt.usernameLabel }}</label>
          <input 
            ref="usernameInputRef"
            v-model="loginForm.username" 
            type="text" 
            autocomplete="username"
            :placeholder="tExt.phUsername" 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-blue-500 focus:bg-white transition-colors font-mono" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ tExt.passwordLabel }}</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            autocomplete="current-password"
            placeholder="••••••••" 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-blue-500 focus:bg-white transition-colors font-mono" 
          />
        </div>
        <p v-if="loginError" class="text-xs text-rose-600 font-bold text-center bg-rose-50 py-2.5 rounded-lg border border-rose-100">{{ loginError }}</p>
        <p v-if="resetMessage" class="text-xs text-emerald-600 font-bold text-center bg-emerald-50 py-2.5 rounded-lg border border-emerald-100">{{ resetMessage }}</p>

        <button type="submit" class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-sm shadow-lg shadow-blue-500/25 transition-all cursor-pointer">
          {{ tExt.loginBtn }}
        </button>
      </form>

      <div class="flex items-center justify-between text-xs pt-4 border-t border-slate-100">
        <button @click="openResetModal" class="text-blue-600 hover:text-blue-800 font-bold cursor-pointer transition-colors">
          {{ tExt.forgotPassword }}
        </button>
        <span class="text-slate-400 font-mono text-[11px] font-semibold">v4.3 Enterprise</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { Cpu } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'

const { t, currentLang } = useI18n()
const {
  loginForm, loginError, resetMessage,
  handleLogin, openResetModal
} = useAuth()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    subtitle: isZh ? 'ERP 权限控制 - 请输入管理员凭证' : isEs ? 'Control de Acceso - Ingrese credenciales' : 'Access Control - Enter credentials',
    usernameLabel: isZh ? '管理员账号' : isEs ? 'Usuario Administrador' : 'Admin Username',
    passwordLabel: isZh ? '管理员密码' : isEs ? 'Contraseña' : 'Admin Password',
    phUsername: isZh ? '请输入用户名' : isEs ? 'Ingrese su usuario' : 'Enter your username',
    loginBtn: isZh ? '安全登录系统' : isEs ? 'Iniciar Sesión Seguro' : 'Secure Login',
    forgotPassword: isZh ? '忘记密码？(重置)' : isEs ? '¿Olvidó su contraseña? (Restablecer)' : 'Forgot password? (Reset)'
  }
})

const usernameInputRef = ref(null)

onMounted(async () => {
  await nextTick()
  if (usernameInputRef.value) {
    usernameInputRef.value.focus()
  }
})
</script>