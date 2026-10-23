// src/utils/api.js
//
// 统一请求层：
//  * 后端地址由 .env 的 VITE_API_BASE 控制，组件里不再硬编码 localhost:8000
//  * 登录后自动携带 Authorization: Bearer <token>
//  * 401 不再“一票否决”直接清 Token：先调用 /api/auth/me 复核，
//    只有确认 Token 失效才清理登录态并通知 UI 回到登录页。

export const API_BASE = import.meta.env.VITE_API_BASE ?? ''

/** 相对路径拼成完整地址；已是 http(s) 绝对地址则原样返回 */
export const apiUrl = (url) => (url?.startsWith('http') ? url : `${API_BASE}${url}`)

// 登录页、请求层、员工/用户缓存必须共用同一套键名
export const AUTH_TOKEN_KEY = 'tostiyk_token'
export const AUTH_LOGGED_IN_KEY = 'tostiyk_logged_in'
export const AUTH_USERNAME_KEY = 'tostiyk_username'
export const AUTH_CURRENT_USER_KEY = 'tostiyk_current_user'

/** 401 复核失败后广播；useAuth 监听后把 isLoggedIn 置 false，显示登录页 */
export const AUTH_EXPIRED_EVENT = 'tostiyk:auth-expired'

const AUTH_PUBLIC_PATHS = ['/api/auth/login', '/api/auth/reset-admin']

export const getToken = () => localStorage.getItem(AUTH_TOKEN_KEY) || ''

export const setToken = (token) => {
  if (token) localStorage.setItem(AUTH_TOKEN_KEY, token)
}

export const clearToken = () => localStorage.removeItem(AUTH_TOKEN_KEY)

/** 清理本地登录态；仅由“确认失效”或主动退出调用 */
export const clearAuthStorage = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(AUTH_LOGGED_IN_KEY)
  localStorage.removeItem(AUTH_USERNAME_KEY)
  localStorage.removeItem(AUTH_CURRENT_USER_KEY)
}

const requestPath = (url) => {
  try {
    return new URL(url, window.location.origin).pathname
  } catch (e) {
    return String(url || '').split('?')[0]
  }
}

const isAuthPublicPath = (url) => AUTH_PUBLIC_PATHS.includes(requestPath(url))

// 同一时刻的多个 401 只发一次 /api/auth/me 复核
let sessionCheckPromise = null

const verifySessionToken = (tokenToCheck) => {
  if (!sessionCheckPromise) {
    sessionCheckPromise = fetch(apiUrl('/api/auth/me'), {
      method: 'GET',
      headers: { Authorization: `Bearer ${tokenToCheck}` },
      cache: 'no-store'
    })
      .then((res) => {
        if (res.ok) return true
        if (res.status === 401) return false
        return null // 后端异常/404/网络问题：不据此踢人
      })
      .catch(() => null)
      .finally(() => {
        sessionCheckPromise = null
      })
  }
  return sessionCheckPromise
}

const notifyAuthExpired = () => {
  // 已经清理过（同一批并发 401 的后到者）就不再重复广播
  const hasSessionMarkers =
    !!getToken() || localStorage.getItem(AUTH_LOGGED_IN_KEY) === 'true'
  if (!hasSessionMarkers) return

  clearAuthStorage()
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(AUTH_EXPIRED_EVENT))
  }
}

export const apiFetch = async (url, options = {}) => {
  const token = getToken()

  // 新增：支持 silent 模式，例如后台轮询、心跳请求不需要全局弹窗
  const silent = options.silent || false
  delete options.silent

  // FormData 必须让浏览器自动带 multipart boundary，不能手动指定 Content-Type
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  }

  // 新增：自动生成并注入 X-Request-Id（防重复提交幂等）
  if (!headers['X-Request-Id']) {
    headers['X-Request-Id'] = typeof crypto !== 'undefined' && crypto.randomUUID 
      ? crypto.randomUUID() 
      : Date.now().toString(36) + Math.random().toString(36).substring(2)
  }

  let response
  try {
    response = await fetch(apiUrl(url), {
      ...options,
      headers
    })
  } catch (error) {
    // 新增：网络断开或跨域失败
    if (!silent) {
      window.dispatchEvent(new CustomEvent('api:global-error', {
        detail: { message: '网络连接异常，请检查网络或服务端', status: 0 }
      }))
    }
    throw error // 必须抛出，因为根本没有 response 对象
  }

  // 登录/重置接口的 401 属于“凭证错误”，不能影响现有登录态
  // 403 权限不足：广播全局事件，由 App.vue 统一弹窗
  if (response.status === 403) {
    window.dispatchEvent(new CustomEvent('auth:forbidden', {
      detail: { url, message: '权限不足，无法执行此操作' }
    }))
  }

  if (response.status === 401 && !isAuthPublicPath(url)) {
    if (!token) {
      if (localStorage.getItem(AUTH_LOGGED_IN_KEY) === 'true') {
        notifyAuthExpired()
      }
    } else {
      const valid = await verifySessionToken(token)
      if (valid === false && getToken() === token) {
        notifyAuthExpired()
      }
    }
  }

  // 新增：拦截 500 等服务器端异常（422 表单验证错误保留给业务组件自己处理，不弹全局）
  if (response.status >= 500 && !silent) {
    window.dispatchEvent(new CustomEvent('api:global-error', {
      detail: { message: `服务器异常 (${response.status})`, status: response.status }
    }))
    // 这里不抛出错误，依然返回 response，让原有的 if(res.ok) 逻辑正常走到 else 分支
  }

  return response
}