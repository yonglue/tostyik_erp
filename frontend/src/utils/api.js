// src/utils/api.js
//
// 统一请求层：
//  * 后端地址由 .env 的 VITE_API_BASE 控制，组件里不再硬编码 localhost:8000
//  * 登录后自动携带 Authorization: Bearer <token>

export const API_BASE = import.meta.env.VITE_API_BASE ?? ''

/** 相对路径拼成完整地址；已是 http(s) 绝对地址则原样返回 */
export const apiUrl = (url) => (url?.startsWith('http') ? url : `${API_BASE}${url}`)

const TOKEN_KEY = 'tostiyk_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY) || ''
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

export const apiFetch = async (url, options = {}) => {
  const token = getToken()

  // FormData 必须让浏览器自动带 multipart boundary，不能手动指定 Content-Type
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  }

  const response = await fetch(apiUrl(url), {
    ...options,
    headers
  })

  // 令牌无效 / 过期：清理本地登录态，由调用方跳回登录页
  if (response.status === 401) {
    clearToken()
    localStorage.removeItem('tostiyk_logged_in')
  }

  return response
}
