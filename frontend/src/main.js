import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 说明：本项目未使用 Element Plus 的任何组件或图标
// （模板中无 el-* 标签、无 ElMessage 等 API，图标统一用 lucide-vue-next），
// 因此不再全局注册它。移除后 CSS 减少约 400 kB。

const app = createApp(App)
app.mount('#app')
