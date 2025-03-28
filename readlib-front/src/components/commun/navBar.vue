<template>
  <div class="navbar lg:px-16">
    <div class="navbar-start">
      <div class="dropdown">
        <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
          </svg>
        </div>
        <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
          <li><a>explore Exams</a></li>
          <li><a>For you</a></li>
          <li><a>About us</a></li>
        </ul>
      </div>

      <router-link :to="{ name: 'exams' }" :class="[logged ? 'text-2xl text-primary' : 'text-2xl text-white']">
        <p>BrevetLib</p>
      </router-link>
    </div>

    <div class="navbar-center hidden lg:flex" v-if="logged">
      <ul class="menu menu-horizontal px-1">
        <li>
          <router-link :to="{ name: 'exams' }">explore Exams</router-link>
        </li>
        <li>
          <router-link :to="{ name: 'exams' }">For you</router-link>
        </li>
        <li><a>About us</a></li>
      </ul>
    </div>

    <div v-if="!logged" class="navbar-end">
      <router-link :to="{ name: 'login' }" class="btn btn-sm pixa-btn btn-primary capitalize flex gap-4">
        <span>login</span>
        <login-icon class="w-5 h-5" />
      </router-link>
    </div>

    <div class="navbar-end" v-if="logged">
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
          <div class="w-10 rounded-full">
            <!-- Bind the image source to the imported variable -->
            <img alt="Tailwind CSS Navbar component" :src="femaleAvatar" />
          </div>
        </div>
        <ul tabindex="0" class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52">
          <li><a>Settings</a></li>
          <li><button @click="useAuth.signOut">Logout</button></li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import loginIcon from '@/assets/icons/loginIcon.vue';
import { useAuthStore } from '@/stores/auth';
import femaleAvatar from '@/assets/images/female.svg';

const useAuth = useAuthStore();
const logged = ref(false);
const route = useRoute();

watch(() => {
  // Check if the current route is 'home'
  logged.value = route.name !== 'home';
});
</script>
