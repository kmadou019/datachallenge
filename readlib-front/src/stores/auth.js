import { reactive,ref } from 'vue'
import { defineStore } from 'pinia'

import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const  isAuthenticated=ref(false)
  const  userId= ref('')
  

  const userToAdd=reactive({
    age:'',
    username:'',
    password:'',
    email:'',
    location:''
  })
  

  const login = async (username, password) => {
    try {
      isAuthenticated.value = true
      //let response = await axios.post('/api/login/', { username, password })
      isAuthenticated.value = true
          router.push({ name: 'exams' })
        
    } catch (error) {
      console.error('Login failed:', error.response ? error.response.data : error.message)
    }
  }
  const register = async () => {
    try {
      let response = await axios.post('/api/inscription/', userToAdd)
      console.log(response.data)
      router.push({ name: 'login' })
    } catch (error) {

      console.error('register failed:', error.response ? error.response.data : error.message)
    }
  }

  const signOut = async () => {
   
    isAuthenticated.value = false
    userId.value = ''
    router.push({ name: 'login' })
  }

  return { userId,isAuthenticated, login, signOut ,userToAdd,register}
})