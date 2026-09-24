export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    apiBase: 'http://127.0.0.1:8000',
  },
  app: {
    head: {
      title: 'ClinicCare · Patient care',
      htmlAttrs: { lang: 'en' },
      meta: [
        {
          name: 'description',
          content: 'Record and review patient consultations with ClinicCare.',
        },
      ],
    },
  },
})
