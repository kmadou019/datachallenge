<template>
    <div class="w-full h-screen flex flex-col items-center gap-4 justify-center">
  
      <div class="w-full sm:w-fit text-2xl text-center mb-4">Register now</div>
  
      <div class="flex items-center gap-4 justify-center w-full h-fit">
  
        <div class="w-full sm:w-fit grid md:grid-cols-2 gap-x-4 gap-y-2">
  
          <div class="form-control w-full sm:w-80 flex flex-col">
            <label class="label">
              <span class="label-text">Username <span class="text-red-500">*</span></span>
            </label>
            <input v-model="useAuth.userToAdd.username"
            type="text" class="block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6" />
          </div>
  
          <div class="form-control w-full sm:w-80 flex flex-col">
            <label class="label">
              <span class="label-text">Email<span class="text-red-500">*</span></span>
            </label>
            <input type="text" 
            v-model="useAuth.userToAdd.email"
            class="block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6" />
          </div>
  
          <div class="form-control w-full sm:w-80 flex flex-col">
            <label class="label">
              <span class="label-text">Age<span class="text-red-500">*</span></span>
            </label>
            <input type="text"
            v-model="useAuth.userToAdd.age"
             class="block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6" />
          </div>
          <div class="form-control w-full sm:w-80 flex flex-col">
            <label class="label">
              <span class="label-text">Location<span class="text-red-500">*</span></span>
            </label>
            <input type="text"
            v-model="useAuth.userToAdd.location"
             class="block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6" />
          </div>
  
          <div class="form-control w-full sm:w-80 flex flex-col">
            <label class="label">
              <span class="label-text">Password <span class="text-red-500">*</span></span>
            </label>
            <input type="password"
            v-model="useAuth.userToAdd.password"
             class="block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset placeholder:text-gray-400 focus:ring-1 focus:ring-inset sm:text-sm sm:leading-6 ring-gray-300 focus:ring-primary" />
            <span class="label-text mt-1 text-xs">Password must be at least 8 characters</span>
          </div>
        </div>
      </div>
      <div class="form-control w-full sm:w-80 flex flex-col">
      <button @click="useAuth.register" class="btn btn-primary w-full mt-2 btn-sm capitalize fill-white flex justify-center flox-col px-10 group">
        Register
        <span v-if="loading" class="loading loading-ring loading-sm"></span>
      </button>
    </div>
    </div>
  </template>
  
  <script setup>
  // Your script setup goes here
  import {useAuthStore} from '@/stores/auth'

const useAuth=useAuthStore()
  </script>
  
  <style lang="scss" scoped>
  /* Your existing styles */
  
  @media (max-width: 640px) {
    .w-full {
      width: auto !important;
    }
    .sm\:w-1\/4 {
      width: 100% !important; /* Full width for small screens */
    }
  }
  </style>
  