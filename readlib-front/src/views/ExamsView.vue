<template>
    <div class="w-full h-full flex flex-col">
      <!-- Top Bar -->
      <div class="w-full">
        <top-bar />
      </div>
  
      <!-- Loading Spinner -->
      <div v-if="loading" class="w-full h-full flex justify-center items-center">
        <span class="loading loading-ring loading-sm"></span>
      </div>
  
      <!-- Questions List -->
      <div v-else class="w-full h-full flex flex-col justify-center items-center">
        <div class="w-full flex flex-col items-center gap-12 justify-center mx-4 my-12">
          <h1 class="text-3xl font-semibold text-gray-800">Exam Questions</h1>
          <p class="text-lg text-gray-600">
            Answer the following questions to the best of your ability.
          </p>
          <!-- Loop over each question -->
          <div
            v-for="(item, index) in localQuestions"
            :key="index"
            class="w-full max-w-4xl p-6 bg-white shadow-lg rounded-2xl border border-gray-200"
          >
            <!-- Question Heading -->
            <h2 class="text-xl mb-4 text-gray-800 break-words whitespace-pre-wrap">
                {{ index + 1 }}. {{ item.Question.heading }}
              </h2>
              <div v-if="item.Question.Options && item.Question.Options.length && isOpen">
                <ul>
                  <li v-for="(option, idx) in item.Question.Options" :key="idx">
                    {{ option }}
                  </li>
                </ul>
              </div>
              
  
            <!-- Open Questions UI -->
            <div v-if="isOpen">
              <textarea
                v-model="item.openAnswer"
                class="w-full p-2 border rounded"
                placeholder="Type your answer here..."
                :disabled="item.answered"
              ></textarea>
              <button
                v-if="!item.answered"
                @click="submitOpenAnswer(item)"
                class="btn btn-primary w-full mt-2 btn-sm pixa-btn capitalize fill-white flex justify-center px-10 group"
              >
                Submit Answer
              </button>
              <div v-if="item.answered" class="mt-4">
                <p class="text-sm text-gray-600">
                  <strong>Evaluation:</strong>
                  {{ item.evaluation || 'Evaluating answer...' }}
                </p>
              </div>
            </div>
  
            <!-- QCM Questions UI -->
            <div v-else>
              <div class="flex flex-col gap-3">
                <button
                  v-for="(option, idx) in item.Question.Options"
                  :key="idx"
                  :disabled="item.selectedIndex !== null"
                  @click="selectAnswer(item, idx)"
                  class="text-left px-4 py-2 rounded-lg border transition-all duration-200"
                  :class="getOptionClass(item, idx)"
                >
                  {{ option }}
                </button>
              </div>
              <div v-if="item.selectedIndex !== null" class="mt-4">
                <p class="text-sm text-gray-600">
                  <strong>Explanation:</strong> {{ getExplanation(item) }}
                </p>
                <p class="text-sm text-gray-500 mt-1">
                  <strong>Legal basis:</strong> {{ getLegalBasis(item) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import topBar from '@/components/commun/navBar.vue';
  import { useExamsStore } from '@/stores/question';
  
  const router = useRouter();
  const useExams = useExamsStore();
  const loading = ref(true);
  const localQuestions = ref([]);
  
  // Use the "question_type" property returned from the backend to determine exam type
  const isOpen = computed(() => useExams.questions.question_type === 'open');
  
  onMounted(() => {
    if (!useExams.questions?.results || useExams.questions.results.length === 0) {
      router.push({ name: 'home' });
    } else {
      localQuestions.value = useExams.questions.results.map(q => ({
        ...JSON.parse(JSON.stringify(q)),
        selectedIndex: null,
        answered: false,
        openAnswer: '',
        evaluation: ''
      }));
      loading.value = false;
    }
  });
  
  // ==================== QCM Functions ====================
  
  function selectAnswer(item, optionIndex) {
    const questionIndex = localQuestions.value.findIndex(q => q === item);
    if (questionIndex === -1) return;
  
    localQuestions.value[questionIndex] = {
      ...localQuestions.value[questionIndex],
      selectedIndex: optionIndex,
      answered: true,
    };
  
    console.log("Selected index for item:", item, "is", optionIndex);
  }
  
  function findCorrectIndex(item) {
    if (!item || !item.Answer) return -1;
  
    if (typeof item.Answer === 'number') {
      return item.Answer >= 0 ? item.Answer : -1;
    }
  
    if (Array.isArray(item.Answer)) {
      return item.Answer.findIndex(ans => ans === true || ans.toString().toLowerCase() === 'true');
    }
  
    if (typeof item.Answer === 'string') {
      const trimmed = item.Answer.trim().toLowerCase();
      const letterMap = { a: 0, b: 1, c: 2, d: 3 };
  
      if (letterMap.hasOwnProperty(trimmed)) {
        return letterMap[trimmed];
      }
  
      if (trimmed === 'true') {
        return 0;
      }
      if (trimmed === 'false') {
        return 1;
      }
  
      const num = parseInt(trimmed);
      return !isNaN(num) && num >= 0 ? num : -1;
    }
  
    return -1;
  }
  
  function getOptionClass(item, idx) {
    if (!item) return 'bg-gray-50 border-gray-300 text-gray-800';
  
    const correctIdx = findCorrectIndex(item);
  
    if (item.selectedIndex === null) {
      return 'bg-gray-50 border-gray-300 hover:bg-gray-100 text-gray-800 cursor-pointer';
    }
  
    // After answer is selected
    if (idx === correctIdx) {
      return 'bg-green-100 border-green-500 text-green-800';
    }
    if (idx === item.selectedIndex && idx !== correctIdx) {
      return 'bg-red-100 border-red-500 text-red-800';
    }
  
    return 'bg-gray-50 border-gray-300 text-gray-500 cursor-default';
  }
  
  function getExplanation(item) {
    if (!item || !item.Explanation) return 'No explanation provided.';
  
    const correctIdx = findCorrectIndex(item);
    if (Array.isArray(item.Explanation) && correctIdx >= 0 && correctIdx < item.Explanation.length) {
      return item.Explanation[correctIdx] || 'No explanation provided.';
    }
  
    return item.Explanation || 'No explanation provided.';
  }
  
  function getLegalBasis(item) {
    if (!item || !item['Legal basis']) return 'Not provided';
  
    const correctIdx = findCorrectIndex(item);
    if (Array.isArray(item['Legal basis']) && correctIdx >= 0 && correctIdx < item['Legal basis'].length) {
      return item['Legal basis'][correctIdx] || 'Not provided';
    }
  
    return item['Legal basis'] || 'Not provided';
  }
  
  // ==================== Open Questions Function ====================
  
  function submitOpenAnswer(item) {
    const questionIndex = localQuestions.value.findIndex(q => q === item);
    if (questionIndex === -1) return;
  
    localQuestions.value[questionIndex].answered = true;
  
    // Combine question heading with options (if available)
    let questionText = item.Question.heading;
    if (item.Question.Options && item.Question.Options.length > 0) {
      questionText += "\nOptions: " + item.Question.Options.join(", ");
    }
  
    const payload = {
      question: questionText,        // Combined question text
      real_answer: item.Answer,        // Correct answer from the dataset
      user_answer: item.openAnswer     // User's provided answer
    };
  
    // Call the evaluateAnswer function from the store (assumed to be defined)
    useExams.evaluateAnswer(payload)
      .then(evaluation => {
        localQuestions.value[questionIndex].evaluation = evaluation;
      })
      .catch(() => {
        localQuestions.value[questionIndex].evaluation = 'Error evaluating answer';
      });
  }
  </script>
  