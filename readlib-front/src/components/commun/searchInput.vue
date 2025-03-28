<template>
    <div class="text-right w-96 h-10 relative overflow-hidden flex items-center">
        <input v-model="searchQuery" type="text" placeholder="type anything..." class="pixa-input-nofloat px-10 w-96 placeholder:capitalize ring-inset focus:ring-0 ">
        <button @click="clearSearch" :class="[searchQuery ? 'opacity-100' : ' opacity-0']"
            class="btn btn-sm btn-square absolute  btn-ghost transition-all right-1 duration-300">
            <times-icon class="w-5 h-5 fill-slate-500 hover:fill-red-500" />
        </button>
        <search-icon :class="[searchQuery ? 'fill-primary' : 'fill-slate-500',

        ]" class="w-5 h-5 absolute left-3" />
    </div>
</template>

<script setup>
import searchIcon from '@/assets/icons/searchIcon.vue'
import { ref, watch } from 'vue'
import timesIcon from '@/assets/icons/timesIcon.vue'


const searchQuery = ref('')
const emits = defineEmits(['searchQuery'])

const clearSearch = () => {
    searchQuery.value = ''
}

watch(() => searchQuery.value, () => {
    emits('searchQuery', searchQuery.value)
})
</script>

<style lang="scss" scoped></style>