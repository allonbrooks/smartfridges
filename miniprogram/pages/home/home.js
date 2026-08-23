const api = require('../../utils/api')

function fmtDate(dateStr) {
  if (!dateStr) return ''
  const d = dateStr.split('T')[0] || dateStr
  return d.slice(5) // "08-23"
}

function fmtDateTime(dtStr) {
  if (!dtStr) return ''
  const d = dtStr.split('T')[0]
  return d.slice(5) // "08-23"
}

Page({
  data: {
    loggedIn: false,
    hasFamily: false,
    showCreateFamily: false,
    familyName: '我的家',
    items: [],
    expiredCount: 0,
    expiringCount: 0,
    safeCount: 0,
    loading: true,
  },

  onShow() {
    if (!this.data.loggedIn) {
      this.initApp()
    } else {
      this.loadOverview()
    }
  },

  async initApp() {
    this.setData({ loading: true })
    try {
      // 1. 登录（自动注册用户）
      const loginRes = await api.users.login()
      if (loginRes.success) {
        this.setData({ loggedIn: true })
        // 2. 检查是否有家庭
        try {
          const familyRes = await api.families.current()
          if (familyRes.success && familyRes.data) {
            this.setData({ hasFamily: true })
            this.loadOverview()
            return
          }
        } catch (e) {
          // 没有家庭，显示创建对话框
        }
        this.setData({ hasFamily: false, showCreateFamily: true, loading: false })
      }
    } catch (e) {
      console.error('init error', e)
      this.setData({ loading: false })
    }
  },

  // 创建家庭
  showCreateDialog() {
    this.setData({ showCreateFamily: true, familyName: '我的家' })
  },

  hideCreateDialog() {
    this.setData({ showCreateFamily: false })
  },

  noop() {},

  onFamilyNameInput(e) {
    this.setData({ familyName: e.detail.value })
  },

  async createFamily() {
    const name = this.data.familyName.trim() || '我的家'
    this.setData({ loading: true })
    try {
      const res = await api.families.create(name)
      if (res.success) {
        wx.showToast({ title: '家庭创建成功', icon: 'success' })
        this.setData({ showCreateFamily: false, hasFamily: true })
        this.loadOverview()
      }
    } catch (e) {
      console.error('create family error', e)
      this.setData({ loading: false })
    }
  },

  async loadOverview() {
    this.setData({ loading: true })
    try {
      const res = await api.items.overview()
      if (res.success) {
        const items = (res.data || []).map(item => ({
          ...item,
          expiryDisplay: item.expiry_date ? item.expiry_date.slice(5) : '',
          createdDisplay: item.created_at ? item.created_at.split('T')[0].slice(5) : '',
        }))
        let expired = 0, expiring = 0, safe = 0
        items.forEach(item => {
          if (item.status === 'red') expired++
          else if (item.status === 'yellow') expiring++
          else safe++
        })
        this.setData({ items, expiredCount: expired, expiringCount: expiring, safeCount: safe })
      }
    } catch (e) {
      console.error('load overview error', e)
    } finally {
      this.setData({ loading: false })
    }
  },

  goSpaces() {
    wx.switchTab({ url: '/pages/spaces/spaces' })
  },

  goAIRecipe() {
    wx.switchTab({ url: '/pages/ai-recipe/ai-recipe' })
  },

  goShopping() {
    wx.switchTab({ url: '/pages/shopping-list/shopping-list' })
  },

  scanBarcode() {
    wx.scanCode({
      success: (res) => {
        wx.showLoading({ title: '查询中...' })
        api.items.barcode(res.code).then(result => {
          wx.hideLoading()
          if (result.success) {
            wx.showToast({ title: '添加成功', icon: 'success' })
            this.loadOverview()
          } else {
            wx.showToast({ title: result.error || '未识别', icon: 'none' })
          }
        }).catch(() => wx.hideLoading())
      }
    })
  },

  voiceInput() {
    wx.showModal({
      title: '语音输入',
      content: '请输入物品名称（如：两盒牛奶、三个番茄）',
      editable: true,
      success: (r) => {
        if (r.confirm && r.content) {
          wx.showLoading({ title: '解析中...' })
          api.items.voice(r.content).then(result => {
            wx.hideLoading()
            if (result.success) {
              wx.showToast({ title: '添加成功', icon: 'success' })
              this.loadOverview()
            }
          }).catch(() => wx.hideLoading())
        }
      }
    })
  },

  onItemTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/space-detail/space-detail?itemId=${id}` })
  },

  onConsume(e) {
    const id = e.currentTarget.dataset.id
    wx.showActionSheet({
      itemList: ['消耗1个', '消耗全部'],
      success: (res) => {
        const quantity = res.tapIndex === 0 ? 1 : 999
        api.items.consume(id, quantity).then(() => {
          wx.showToast({ title: '已消耗', icon: 'success' })
          this.loadOverview()
        })
      }
    })
  },
})