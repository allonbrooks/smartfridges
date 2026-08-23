// API 请求封装
const app = getApp()

// 开发环境 mock OpenID（云托管正式环境会由网关自动注入真实值）
const DEV_OPENID = 'dev_user_' + Date.now()

function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: app.globalData.baseUrl + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'content-type': 'application/json',
        'X-WX-OPENID': DEV_OPENID,
        ...options.headers,
      },
      success(res) {
        if (res.statusCode === 200 || res.statusCode === 201) {
          resolve(res.data)
        } else if (res.statusCode === 401 || (res.statusCode === 404 && res.data?.error?.includes('家庭'))) {
          // 未登录/未加入家庭 - 让页面自己处理，不弹 toast
          reject(res.data)
        } else {
          wx.showToast({ title: res.data?.error || '请求失败', icon: 'none' })
          reject(res.data)
        }
      },
      fail(err) {
        wx.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      }
    })
  })
}

// 用户 & 家庭 API
const users = {
  login: () => request('/api/users/login', { method: 'POST' }),
}

const families = {
  create: (name) => request('/api/families', { method: 'POST', data: { name } }),
  current: () => request('/api/families/current'),
}

// 空间 API
const spaces = {
  list: () => request('/api/spaces'),
  create: (name, type) => request('/api/spaces/create', { method: 'POST', data: { name, type } }),
  detail: (id) => request(`/api/spaces/${id}`),
}

// 物品 API
const items = {
  overview: () => request('/api/items/overview'),
  list: (params) => request('/api/items', { data: params }),
  create: (data) => request('/api/items/create', { method: 'POST', data }),
  batchCreate: (data) => request('/api/items/batch', { method: 'POST', data }),
  detail: (id) => request(`/api/items/${id}`),
  consume: (id, quantity) => request(`/api/items/${id}/consume`, { method: 'PATCH', data: { quantity } }),
  delete: (id) => request(`/api/items/${id}/delete`, { method: 'DELETE' }),
  barcode: (code) => request('/api/items/barcode', { method: 'POST', data: { barcode: code } }),
  voice: (text) => request('/api/items/voice', { method: 'POST', data: { raw_text: text } }),
}

// 菜谱 API
const recipes = {
  generate: (itemIds) => request('/api/recipes/generate', { method: 'POST', data: { item_ids: itemIds } }),
}

// 购物清单 API
const shopping = {
  list: () => request('/api/shopping-list'),
  create: (data) => request('/api/shopping-list/add', { method: 'POST', data }),
  toggle: (id, is_purchased) => request(`/api/shopping-list/${id}/purchased`, { method: 'PATCH', data: { is_purchased } }),
  delete: (id) => request(`/api/shopping-list/${id}/delete`, { method: 'DELETE' }),
  clearChecked: () => request('/api/shopping-list/clear-checked', { method: 'DELETE' }),
}

module.exports = { request, users, families, spaces, items, recipes, shopping }