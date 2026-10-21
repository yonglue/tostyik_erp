<!-- src/components/SideDrawer.vue -->
<template>
  <div v-if="visible" class="fixed inset-0 z-50">
    <!-- 遮罩层 -->
    <div 
      @click="$emit('close')" 
      class="absolute inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
    ></div>
    
    <!-- 右侧面板 -->
    <div 
      class="absolute right-0 top-0 h-full w-full bg-white shadow-2xl flex flex-col transition-transform duration-300"
      :class="widthClass"
    >
      <!-- 头部 -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-xl">{{ icon }}</span>
          <h3 class="font-bold text-slate-800 text-base">{{ title }}</h3>
        </div>
        <div class="flex items-center gap-2">
          <!-- 插槽：头部右侧按钮组（如只读态的编辑/删除按钮） -->
          <slot name="header-actions"></slot>
          
          <!-- 关闭按钮 -->
          <button 
            @click="$emit('close')" 
            class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 内容区（可滚动） -->
      <div class="flex-1 overflow-y-auto">
        <slot></slot>
      </div>

      <!-- 插槽：底部操作区（如编辑态的取消/保存按钮） -->
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: '📋'
  },
  widthClass: {
    type: String,
    default: 'max-w-[560px]' // 默认宽度，可通过 props 覆盖
  }
})

defineEmits(['close'])
</script>