<template>
  <div class="w-full h-full flex flex-col items-center gap-4 justify-center">
  <div  class="flex  items-center gap-4 justify-center w-[350px]  h-screen">
   
           <div v-if="loadingPage" class="w-full grow flex items-center justify-center">
               <span class="loading loading-ring loading-sm"></span>
           </div>

           <div v-else class="w-full flex flex-col gap-2 items-center justify-center">
            <a className=" pixa-title text-2xl ">ReadLib</a>
               <div class="form-control w-full flex flex-col">
                   <label class="label">
                       <span class="label-text">username</span>
                   </label>
                   <div class="w-full h-fit relative flex items-center">
                   <input type="text" v-model="user.username"
                   class=" pr-12 block w-full h-10 rounded-md border-0 py-1.5  text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6" />

                   <button class="right-1 btn btn-sm btn-square rounded absolute  btn-ghost">
               <user-icon class="w-4 h-4 fill-slate-400" />
              </button>
                   </div>
               </div>
               <div class="form-control w-full">
                   <label class="label">
                       <span class="label-text">mot de passe</span>
                   </label>

                   <div class="w-full h-fit relative flex items-center">
                       <input :type="isPassword ? 'password' : 'text'" @keypress.enter="login" v-model="user.password"
                           class=" pr-12 block w-full h-10 rounded-md border-0 py-1.5  text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6" />

                       <button @click="isPassword = !isPassword" class="right-1 btn btn-sm btn-square rounded absolute  btn-ghost">
                           <eye-icon v-if="isPassword" class="w-4 h-4 fill-slate-400" />
                           <eye-slash v-else class="w-4 h-4 fill-slate-400" />
                       </button>
                   </div>

                   <label class="label">
                       <span></span>
                       <span class="label-text">mot de passe oublié</span>
                   </label>
               </div>

               <button @click="login"
                   class="btn btn-primary w-full mt-2 btn-sm pixa-btn capitalize fill-white flex justify-center px-10 group">
                  se connecter
                   <span v-if="loading" class="loading loading-ring loading-sm"></span>
                   <arrow-right v-else class="rotate-0  -translate-x-0  
                       w-5 h-5 transition-all duration-300 group-hover:translate-x-8" />

               </button>
               <div className="divider">OR</div>

             <router-link class="w-full h-fit relative flex items-center" :to="{ name: 'register' }">
                   <button 
                   class=" block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300  focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6" >
Register now
             </button>
                   </router-link>
           </div>
          </div>
       </div>

      
  
</template>

<script setup>
import arrowRight from '@/assets/icons/arrowRight.vue'

import {   ref , onMounted} from 'vue'
import { useRouter } from 'vue-router'
import userIcon from '@/assets/icons/userIcon.vue'
import eyeIcon from '../../assets/icons/eyeIcon.vue'
import eyeSlash from '@/assets/icons/eyeSlash.vue'

import axios from 'axios'
import {useAuthStore} from '@/stores/auth'
const router=useRouter()
const useAuth=useAuthStore()
const loading = ref(false)
const isPassword = ref(true)
const loadingPage = ref(false)

const user = ref(
   {
      username: '',
       password: ''
   }
)


const login = () => {
   loading.value = true
   axios.defaults.headers.common["Authorization"] = ""
   useAuth.login(user.value.username, user.value.password)
}

onMounted(async () => {
   
   if (useAuth.isAuthenticated) {
       router.push({ name: 'exams' })
   }
   else {
       setTimeout(() => {
           loadingPage.value = false
       }, 500)
   }
})
</script>

<style lang="scss" scoped></style>