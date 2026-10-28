import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, getUserInfo, logout } from '@/api/user'
import { getToken, removeToken, setToken } from '@/utils/auth'
import defAva from '@/static/images/rescue/avatar.png'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken())
  const phone = ref('')
  const avatar = ref(defAva)

  let pending = null

  // 演示版无登录页：没有 token 时自动登录，再拉取用户信息
  const ensureLogin = () => {
    if (!pending) {
      pending = (token.value ? Promise.resolve() : login({}).then(res => {
        setToken(res.token)
        token.value = res.token
      })).then(getUserInfo).then(user => {
        phone.value = user.phone
        avatar.value = user.avatar || defAva
        return user
      }).catch(err => {
        pending = null
        throw err
      })
    }
    return pending
  }

  const logOut = () => {
    return logout().finally(() => {
      token.value = ''
      phone.value = ''
      pending = null
      removeToken()
    })
  }

  return { token, phone, avatar, ensureLogin, logOut }
})
