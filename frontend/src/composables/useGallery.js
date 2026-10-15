// src/composables/useGallery.js
//
// 商品图片查看器状态（放大预览 / 上一张 / 下一张）。

import { ref } from 'vue'

const galleryModalVisible = ref(false)
const currentGalleryImages = ref([])
const currentGalleryIndex = ref(0)

export function useGallery() {
  const openGallery = (images, index) => {
    currentGalleryImages.value = images
    currentGalleryIndex.value = index
    galleryModalVisible.value = true
  }

  const prevGalleryImage = () => {
    if (currentGalleryImages.value.length === 0) return
    currentGalleryIndex.value =
      (currentGalleryIndex.value - 1 + currentGalleryImages.value.length) %
      currentGalleryImages.value.length
  }

  const nextGalleryImage = () => {
    if (currentGalleryImages.value.length === 0) return
    currentGalleryIndex.value =
      (currentGalleryIndex.value + 1) % currentGalleryImages.value.length
  }

  return {
    galleryModalVisible,
    currentGalleryImages,
    currentGalleryIndex,
    openGallery,
    prevGalleryImage,
    nextGalleryImage
  }
}
