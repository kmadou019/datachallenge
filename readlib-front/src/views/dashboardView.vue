<template>
  <div class="w-full h-full flex flex-col">
    <div class="w-full">
      <top-bar />
    </div>

    <!-- Modal for Adding Category -->
    <div v-if="showModal" class="flex justify-center items-center h-screen w-screen fixed top-0 left-0 bg-opacity-50 bg-gray-900 z-50">
      <div v-if="loading" class="w-full h-full flex justify-center items-center">
        <span class="loading loading-ring loading-sm"></span>
      </div>
      <div v-else class="bg-white rounded-lg p-5 w-1/3">
        <h2 class="text-black text-2xl font-bold mb-5" @dblclick.prevent style="user-select: none">
          Bienvenue au BrevetLib
        </h2>
        <hr />
        <p class="text-black my-4 text-sm w-full" @dblclick.prevent style="user-select: none">
          Veuillez spécifier le domaine que vous voulez réviser
        </p>
        <div class="relative w-full">
          <select
            v-model="category"
            id="category-input"
            class="pr-12 block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
          >
            <option disabled value="">Select an option</option>
            <option value="qcm">qcm</option>
            <option value="open">open questions</option>
          </select>
          <label
            for="category-input"
            class="absolute text-sm text-gray-500 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 left-1"
          >
            Mots clés
          </label>
        </div>
        <p class="text-black text-sm mt-6" @dblclick.prevent style="user-select: none">
          Vous pouvez ajouter des mots clés pour votre domaine
        </p>
        <!-- Keywords Input Section -->
        <div class="flex flex-row mt-3 space-x-2 w-full">
          <div class="relative w-full">
            <input
              v-model="subCategory"
              type="text"
              id="sub-category-input"
              class="pr-12 block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
              placeholder=" "
            />
            <label
              for="sub-category-input"
              class="absolute text-sm text-gray-500 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 left-1"
            >
              Mots clés
            </label>
          </div>
          <div>
            <button
              @click="addSubCategory"
              class="btn btn-primary w-full btn-sm pixa-btn capitalize fill-white flex justify-center px-10 group"
            >
              Ajouter
            </button>
          </div>
        </div>
        <!-- Display Added Subcategories -->
        <div class="mt-3 flex flex-wrap gap-2">
          <span
            v-for="subCat in subCategories"
            :key="subCat"
            class="bg-primary text-white px-3 py-1 rounded-full flex items-center space-x-2"
          >
            <span>{{ subCat }}</span>
            <button @click="deleteSubCategory(subCat)" class="text-white">x</button>
          </span>
        </div>
        <!-- Modal Buttons -->
        <div class="flex flex-row mt-5 justify-end gap-3">
          <button
            @click="toggleModal"
            class="btn btn-ghost btn-sm pixa-btn capitalize fill-white flex justify-center px-10 group"
          >
            Cancel
          </button>
          <button
            @click="addCategory"
            class="btn btn-primary btn-sm pixa-btn capitalize fill-white flex justify-center px-10 group"
          >
            Search
          </button>
        </div>
      </div>
    </div>

    <!-- The rest of your page content goes here -->
  </div>
</template>

<script setup>
import topBar from '@/components/commun/navBar.vue';
import { ref } from 'vue';
import { useExamsStore } from '@/stores/question';
import router from '@/router';

const useexams = useExamsStore();
const showModal = ref(true);
const category = ref('');
const subCategory = ref('');
const subCategories = ref([]);
const loading = ref(false); // loading state

const addSubCategory = () => {
  if (subCategory.value.trim() !== '') {
    subCategories.value.push(subCategory.value.trim());
    subCategory.value = '';
  }
};

const deleteSubCategory = (subCat) => {
  subCategories.value = subCategories.value.filter((cat) => cat !== subCat);
};

const addCategory = async () => {
  // Require both a selected category and at least one keyword
  if (!category.value.trim() || subCategories.value.length === 0) return;

  // Combine keywords into a single query string
  const queryStr = subCategories.value.join(' ');
  
  // Set loading to true before starting the API call
  loading.value = true;
  await useexams.getQuestions(category.value, queryStr);
  // Once the API call is finished, set loading to false and close the modal
  loading.value = false;
  showModal.value = false;
};

const toggleModal = () => {
  showModal.value = !showModal.value;
};
</script>
