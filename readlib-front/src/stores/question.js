import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import router from '@/router'

export const useExamsStore = defineStore('exams', () => {
  
  const questions = ref([])
  const similar_query = ref({})
  const generated_query = ref('')

  const getQuestions = async (question_type = 'qcm', query = 'loss of right', k = 5, mode = 'exam', export_pdf = false) => {
    console.log('getQuestions:', question_type, query, k, mode, export_pdf)
    try {
      if (export_pdf) {
        const response = await axios.get(`http://127.0.0.1:8000/search`, {
          params: { question_type, query, k, mode, export_pdf },
          responseType: 'blob'
        })
  
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'questions.pdf')
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
  
        return { downloaded: true }
      } else {
        const response = await axios.get(`http://127.0.0.1:8000/search`, {
          params: { question_type, query, k, mode, export_pdf }
        })
  
        questions.value = response.data
  
        if (questions.value.length === 0) {
          console.log('No questions found for query:', query)
        } else {
          router.push({ name: 'exam', params: { questions: questions.value } })
        }
  
        return { downloaded: false }
      }
    } catch (error) {
      console.error('Error fetching questions:', error)
      return { error: true }
    }
  }
  

  const getLegalQuery = async (query) => {  
    try {
      const response = await fetch('http://localhost:8000/legal_query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query}),
      });
      const data = await response.json();
      console.log('Legal Query Response:', data);
      if (data.found_similar) {
        console.log('Similar question found:', data.similar_question);
        similar_query.value = data.similar_question
        router.push({ name    : 'question',    // name of the route
          params  : { querys: similar_query.value } }) // params for the route
        // You can update your state/store here if needed
      }
      else {
        console.log('No similar question found');
        generated_query.value = data.generated_explanation
        router.push({ name    : 'question',    // name of the route
          params  : { querys: generated_query.value } }) // params for the route
        // You can update your state/store here if needed
      }
      
    } catch (error) {
      console.error('Error calling /legal_query:', error);
    }
  }
  const evaluateAnswer = async (payload) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/evaluate', payload)
      return {
        evaluation: response.data.evaluation,
        emission: response.data.emission
      }
    } catch (error) {
      console.error('Error evaluating answer:', error)
      return {
        evaluation: 'Error evaluating answer',
        emission: null
      }
    }
  }
  

  return {
    questions,
    getQuestions,
    evaluateAnswer,
    getLegalQuery,
    similar_query,
    generated_query
  }
})
