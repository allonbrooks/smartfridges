const api = require('../../utils/api')

const TYPE_ICONS = {
  cold: '🥶',
  frozen: '🧊',
  normal: '🗄️',
}

Page({
  data: {
    spaces: [],
    loading: true,
    showCreate: false,
    newName: '',
    newType: 'cold',
    newTypeLabel: '🥶 冷藏区',
    typeOptions: [
      { value: 'cold', label: '🥶 冷藏区' },
      { value: 'frozen', label: '🧊 冷冻区' },
      { value: 'normal', label: '🗄️ 常温区' },
    ],
    typeIndex: 0,
  },

  onShow() {
    this.loadSpaces()
  },

  async loadSpaces() {
    this.setData({ loading: true })
    try {
      const res = await api.spaces.list()
      if (res.success) {
        const spaces = (res.data || []).map(s => ({
          ...s,
          typeIcon: TYPE_ICONS[s.zone_type] || '📦',
        }))
        this.setData({ spaces })
      }
    } catch (e) {
      console.error('load spaces error', e)
    } finally {
      this.setData({ loading: false })
    }
  },

  showCreateDialog() {
    this.setData({ showCreate: true, newName: '', newType: 'cold', newTypeLabel: '🥶 冷藏区', typeIndex: 0 })
  },

  hideCreateDialog() {
    this.setData({ showCreate: false })
  },

  noop() {},

  onNameInput(e) {
    this.setData({ newName: e.detail.value })
  },

  onTypeChange(e) {
    const idx = e.detail.value
    const opt = this.data.typeOptions[idx]
    this.setData({ newType: opt.value, newTypeLabel: opt.label, typeIndex: idx })
  },

  async createSpace() {
    if (!this.data.newName.trim()) {
      wx.showToast({ title: '请输入名称', icon: 'none' })
      return
    }
    try {
      const res = await api.spaces.create(this.data.newName.trim(), this.data.newType)
      if (res.success) {
        wx.showToast({ title: '创建成功', icon: 'success' })
        this.hideCreateDialog()
        this.loadSpaces()
      }
    } catch (e) {
      console.error('create space error', e)
    }
  },

  goSpaceDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/space-detail/space-detail?spaceId=${id}` })
  },
})