<!-- Choose contentType as 'explanation' or 'exam', and category as 'qcm' or 'open' -->
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

        <!-- Content Type -->
        <div class="relative w-full mb-4">
          <select
            v-model="contentType"
            id="content-type-input"
            class="pr-12 block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
          >
            <option disabled value="">Select an option</option>
            <option value="exam">Exams</option>
            <option value="explanation">Explanation</option>
          </select>
          <label
            for="content-type-input"
            class="absolute text-sm text-gray-500 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 left-1"
          >
            Type de contenu
          </label>
        </div>

        <!-- Category Type -->
        <p  v-if="contentType !== 'explanation'" class="text-black my-2 text-sm w-full" @dblclick.prevent style="user-select: none">
          Veuillez spécifier le type de questions
        </p>
        <div v-if="contentType !== 'explanation'" class="relative w-full mb-4">
          <select
            v-model="category"
            id="category-type-input"
            class="pr-12 block w-full h-10 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
          >
            <option disabled value="">Select an option</option>
            <option value="qcm">QCM</option>
            <option value="open">Open Questions</option>
          </select>
          <label
            for="category-type-input"
            class="absolute text-sm text-gray-500 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 left-1"
          >
            Type de questions
          </label>
        </div>

<!-- Keywords Input Section -->
<p class="text-black text-sm mt-4" @dblclick.prevent style="user-select: none">
  Vous pouvez ajouter des mots clés pour votre domaine
</p>

<!-- Show textarea when contentType is 'explanation' -->
<div v-if="contentType === 'explanation'" class="relative w-full mt-3">
  <textarea
    v-model="descriptionText"
    id="description-textarea"
    rows="5"
    class="block w-full rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-1 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
    placeholder="Entrez une description..."
  ></textarea>
</div>

<!-- Otherwise, show keyword input with add button -->
<div v-else class="flex flex-row mt-3 space-x-2 w-full">
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

<!-- Display Added Keywords -->
<div v-if="contentType !== 'explanation'" class="mt-3 flex flex-wrap gap-2">
  <span
    v-for="subCat in subCategories"
    :key="subCat"
    class="bg-primary text-white px-3 py-1 rounded-full flex items-center space-x-2"
  >
    <span>{{ subCat }}</span>
    <button @click="deleteSubCategory(subCat)" class="text-white">x</button>
  </span>
</div>
<!-- Export PDF Option -->
<div  class="mt-4">
  <p class="text-sm font-medium text-gray-700 mb-2">Exporter en PDF ?</p>
  <div class="flex items-center space-x-4">
    <label class="flex items-center space-x-2">
      <input type="radio" v-model="exportAsPDF" :value="true" />
      <span>Oui</span>
    </label>
    <label class="flex items-center space-x-2">
      <input type="radio" v-model="exportAsPDF" :value="false" />
      <span>Non</span>
    </label>
  </div>
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
  </div>
</template>

<script setup>
import topBar from '@/components/commun/navBar.vue';
import { ref } from 'vue';
import { useExamsStore } from '@/stores/question';

const useexams = useExamsStore();

const showModal = ref(true);
const category = ref('');
const contentType = ref('');
const subCategory = ref('');
const subCategories = ref([]);
const loading = ref(false);
const descriptionText = ref('');
const exportAsPDF = ref(false)


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
  if (
    !contentType.value ||
    (contentType.value !== 'explanation' && subCategories.value.length === 0) ||
    (contentType.value === 'explanation' && !descriptionText.value.trim())
  ) return;

  const queryStr =
    contentType.value === 'explanation'
      ? descriptionText.value.trim()
      : subCategories.value.join(' ')

  loading.value = true

  if (contentType.value === 'explanation') {
    await useexams.getLegalQuery(queryStr)
  } else {
    await useexams.getQuestions(
      category.value,
      queryStr,
      5,
      contentType.value,  // 'exam'
      exportAsPDF.value    // pass true/false based on selection
    )
  }

  loading.value = false
  showModal.value = false
}



const toggleModal = () => {
  showModal.value = !showModal.value;
};
</script>
