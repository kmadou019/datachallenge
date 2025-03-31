<script setup>
import { onMounted, ref } from 'vue'
import { useExamsStore } from '@/stores/question';

const examsStore = useExamsStore()
const displayData = ref(null)
const isFromDB = ref(false)
onMounted(() => {
  // Prefer similar_query if available
  if (examsStore.similar_query?.Question) {
    displayData.value = examsStore.similar_query
    isFromDB.value = true
  } else if (examsStore.generated_query) {
    displayData.value = examsStore.generated_query
  } else {
    displayData.value = null
  }
})
</script>

<template>
    <div class="w-full h-full flex flex-col">
      <!-- Top Bar -->
      <div class="w-full">
        <top-bar />
      </div>
  
      <!-- Explanation Content -->
      <div class="w-full h-full flex flex-col justify-center items-center">
        <div class="w-full flex flex-col items-center gap-12 justify-center mx-4 my-12">
          <h1 class="text-3xl font-semibold text-gray-800">Your Explanation</h1>
          <p class="text-lg text-gray-600" v-if="!isFromDB">
            This explanation is generated for you by the Mistral 7B model.
          </p>
          <p class="text-lg text-gray-600" v-else>
            A Similar question was found in the database.
          </p>
  
          <div class="w-full max-w-4xl p-6 bg-white shadow-lg rounded-2xl border border-gray-200 space-y-6">
            <!-- Similar Question Display -->
            <template v-if="displayData?.Question">
              <div>
                <h2 class="text-xl text-gray-800 font-semibold mb-2">Question</h2>
                <p class="text-gray-700 whitespace-pre-wrap break-words">
                  {{ displayData.Question.heading }}
                </p>
              </div>
  
              <div v-if="displayData.Question.Options?.length">
                <h2 class="text-lg font-medium text-gray-800">Options</h2>
                <ul class="list-disc ml-5 text-gray-700">
                  <li v-for="(option, idx) in displayData.Question.Options" :key="idx">
                    {{ option }}
                  </li>
                </ul>
              </div>
  
              <div>
                <h2 class="text-lg font-medium text-gray-800">Answer</h2>
                <p class="text-green-700 whitespace-pre-wrap break-words">
                  {{ displayData.Answer }}
                </p>
              </div>
  
              <div>
                <h2 class="text-lg font-medium text-gray-800">Explanation</h2>
                <p class="text-gray-700 whitespace-pre-wrap break-words">
                  {{ displayData.Explanation }}
                </p>
              </div>
  
              <div>
                <h2 class="text-lg font-medium text-gray-800">Legal Basis</h2>
                <p class="text-gray-700 whitespace-pre-wrap break-words">
                  {{ displayData['Legal basis'] }}
                </p>
              </div>
            </template>
  
            <!-- Generated Explanation Display -->
            <template v-else-if="displayData">
              <div>
                <h2 class="text-lg font-medium text-gray-800">Generated Explanation</h2>
                <p class="text-gray-700 whitespace-pre-wrap break-words">
                  {{ displayData }}
                </p>
              </div>
            </template>
  
            <!-- Fallback: No data -->
            <template v-else>
              <div>
                <h2 class="text-lg font-medium text-red-700">No explanation available.</h2>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </template>
  