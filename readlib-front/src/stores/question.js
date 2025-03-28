import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import router from '@/router'

export const useExamsStore = defineStore('exams', () => {
  
  const questions = ref([])

  const getQuestions = async (question_type= 'qcm', query = 'loss of right', k = 5, mode = 'exam', export_pdf = false) => {
    console.log('getQuestions:', question_type, query, k, mode, export_pdf)
    try {
      let response = await axios.get(`http://127.0.0.1:8000/search`, {
        params: {
          question_type,
          query,
          k,
          mode,
          export_pdf
        }
      })
      questions.value = response.data
      console.log(questions.value)
        if (questions.value.length === 0 ){
          console.log('No questions found for query:', query)
        }
        else {
          router.push({ name    : 'exam',    // name of the route
                        params  : { questions: questions.value } }) // params for the route
        }
    } catch (error) {
      console.error('Error fetching questions:', error)
    }
  }
  const evaluateAnswer = async (payload) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/evaluate', payload)
      return response.data.evaluation
    } catch (error) {
      console.error('Error evaluating answer:', error)
      return 'Error evaluating answer'
    }
  }

  return {
    questions,
    getQuestions,
    evaluateAnswer
  }
})
