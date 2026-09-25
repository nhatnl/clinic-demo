<script setup lang="ts">
import type { Diagnosis, Page, PatientRecord } from '~/types/clinic'
useHead({ title: 'New consultation · ClinicCare' })
const { session } = useAuth()
const route = useRoute()
const initialPatientId =
  Number.isInteger(Number(route.query.patient_id)) && Number(route.query.patient_id) > 0
    ? Number(route.query.patient_id)
    : ''
const patientId = ref<number | ''>(initialPatientId)
const patientSearch = ref('')
const suggestionsOpen = ref(false)
const activeSuggestion = ref(-1)
const selectedPatient = ref<PatientRecord | null>(null)
const { data: patients, status: patientsStatus, error: patientsError, refresh: refreshPatients } =
  await useFetch<Page<PatientRecord>>('/api/patients', {
    query: computed(() => ({ page: 1, page_size: 20, ...(patientSearch.value.trim() ? { name: patientSearch.value.trim() } : {}) })),
    default: () => ({ items: [], total: 0, page: 1, page_size: 20 }),
  })
const visiblePatients = computed(() => patients.value.items)
if (initialPatientId) {
  selectedPatient.value = patients.value.items.find((patient) => patient.id === initialPatientId) || null
  if (!selectedPatient.value) {
    try {
      selectedPatient.value = await useRequestFetch()<PatientRecord>(`/api/patients/${initialPatientId}`)
    } catch {
      // The form still requires the user to choose a patient.
    }
  }
  if (selectedPatient.value)
    patientSearch.value = `${selectedPatient.value.first_name} ${selectedPatient.value.last_name}`
}
watch(patients, () => {
  activeSuggestion.value = -1
})
const activePatient = computed(() => visiblePatients.value[activeSuggestion.value])
const showPatientForm = ref(false)
const createdPatient = ref<PatientRecord | null>(null)
const notes = ref('')
const diagnoses = ref<Diagnosis[]>([])
const pending = ref(false)
const saved = ref(false)
const error = ref('')
const dirty = computed(
  () =>
    !saved.value &&
    Boolean(
      patientId.value !== initialPatientId ||
      notes.value ||
      diagnoses.value.length,
    ),
)
function selectDiagnosis(item: Diagnosis) {
  if (!diagnoses.value.some((selected) => selected.code === item.code))
    diagnoses.value.push(item)
}
function selectPatient(patient: PatientRecord) {
  patientId.value = patient.id
  selectedPatient.value = patient
  patientSearch.value = `${patient.first_name} ${patient.last_name}`
  suggestionsOpen.value = false
}
function openSuggestions() {
  suggestionsOpen.value = true
  activeSuggestion.value = -1
}
function onPatientInput() {
  patientId.value = ''
  selectedPatient.value = null
  openSuggestions()
}
function onPatientKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    suggestionsOpen.value = false
    return
  }
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
    suggestionsOpen.value = true
    if (!visiblePatients.value.length) return
    const direction = event.key === 'ArrowDown' ? 1 : -1
    activeSuggestion.value = activeSuggestion.value < 0
      ? (direction === 1 ? 0 : visiblePatients.value.length - 1)
      : (activeSuggestion.value + direction + visiblePatients.value.length) % visiblePatients.value.length
  }
  if (event.key === 'Enter' && suggestionsOpen.value && activeSuggestion.value >= 0) {
    event.preventDefault()
    selectPatient(visiblePatients.value[activeSuggestion.value]!)
  }
}
function onPatientFocusOut(event: FocusEvent) {
  if (!(event.currentTarget as HTMLElement).contains(event.relatedTarget as Node | null))
    suggestionsOpen.value = false
}
function onPatientCreated(patient: PatientRecord) {
  selectPatient(patient)
  createdPatient.value = patient
  showPatientForm.value = false
}
async function submit() {
  if (pending.value || saved.value) return
  error.value = ''
  if (patientId.value === '' || !selectedPatient.value) {
    error.value = 'Select a patient before saving the consultation.'
    return
  }
  if (!diagnoses.value.length) {
    error.value = 'Please select at least one diagnosis code.'
    return
  }
  if (!notes.value.trim()) {
    error.value = 'Please enter treatment notes.'
    return
  }
  pending.value = true
  try {
    await $fetch('/api/consultation', {
      method: 'POST',
      body: {
        patient_id: Number(patientId.value),
        diagnosis_codes: diagnoses.value.map((item) => item.code),
        note: notes.value.trim(),
      },
    })
    saved.value = true
    clearNuxtData()
    await navigateTo('/consultations?created=1')
  } catch (cause) {
    error.value = errorMessage(cause)
  } finally {
    pending.value = false
  }
}
function beforeUnload(event: BeforeUnloadEvent) {
  if (dirty.value) {
    event.preventDefault()
    event.returnValue = ''
  }
}
onMounted(() => window.addEventListener('beforeunload', beforeUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
onBeforeRouteLeave(() => {
  if (!session.value) return true
  if (pending.value && !saved.value) return false
  if (
    dirty.value &&
    !window.confirm(
      'You have unsaved changes. Leave this page and discard them?',
    )
  )
    return false
})
</script>
<template>
  <NuxtLink to="/consultations" class="back-link"
    >← Consultation history</NuxtLink
  >
  <div class="page-heading">
    <div>
      <span class="eyebrow">DOCUMENT A VISIT</span>
      <h1>New consultation<span class="heading-dot">.</span></h1>
      <p>
        Capture patient details, diagnoses, and the next steps in their care.
      </p>
    </div>
    <span class="draft-badge">{{ saved ? 'Saved' : 'Unsaved' }}</span>
  </div>
  <div class="consultation-form">
    <fieldset :disabled="pending || saved" class="form-fields">
      <section class="card form-section patient-section">
        <div class="section-title">
          <span class="section-number">01</span>
          <div>
            <h2>Patient details</h2>
            <p>Link this visit to an existing or newly created patient record.</p>
          </div>
        </div>
        <div class="field patient-picker" @focusout="onPatientFocusOut">
          <div class="patient-picker-heading">
            <label for="patient-search">Patient <span class="required">*</span></label>
            <button v-if="session && [1, 2, 3].includes(session.role)" type="button" class="text-button" :disabled="pending || saved" @click="suggestionsOpen = false; showPatientForm = !showPatientForm">
              <AppIcon name="plus" />{{ showPatientForm ? 'Close new patient form' : 'New patient' }}
            </button>
          </div>
          <div class="patient-combobox">
            <input
              id="patient-search"
              v-model="patientSearch"
              type="search"
              form="consultation-form"
              required
              maxlength="50"
              autocomplete="off"
              role="combobox"
              aria-autocomplete="list"
              aria-controls="patient-suggestions"
              :aria-expanded="suggestionsOpen"
              :aria-activedescendant="suggestionsOpen && activePatient ? `patient-option-${activePatient.id}` : undefined"
              :placeholder="patientsStatus === 'pending' ? 'Loading patients…' : 'Search by first or last name…'"
              @focus="openSuggestions"
              @input="onPatientInput"
              @keydown="onPatientKeydown"
            />
            <div v-if="suggestionsOpen && patientsStatus !== 'pending' && !patientsError" id="patient-suggestions" class="patient-suggestions" role="listbox" aria-label="Patients">
              <button
                v-for="(patient, index) in visiblePatients"
                :id="`patient-option-${patient.id}`"
                :key="patient.id"
                type="button"
                role="option"
                class="patient-suggestion"
                :class="{ active: activeSuggestion === index }"
                :aria-selected="patientId === patient.id"
                @pointerdown.prevent="selectPatient(patient)"
                @click="selectPatient(patient)"
              >
                <span>{{ patient.first_name }} {{ patient.last_name }}</span>
                <small>Patient #{{ patient.id }} · {{ patient.age }} years</small>
              </button>
              <p v-if="!visiblePatients.length" class="patient-suggestions-empty">No patients found. Create a new patient if needed.</p>
            </div>
          </div>
          <p v-if="selectedPatient" class="field-hint">Selected: {{ selectedPatient.first_name }} {{ selectedPatient.last_name }} · Patient #{{ selectedPatient.id }}</p>
        </div>
        <ApiFeedback v-if="patientsError" :error="patientsError" @retry="refreshPatients()" />
        <div v-if="createdPatient?.id === patientId" class="notice success" role="status">
          {{ createdPatient.first_name }} {{ createdPatient.last_name }} created. Patient #{{ createdPatient.id }} is selected for this consultation.
        </div>
      </section>
    </fieldset>
    <PatientCreateForm v-if="showPatientForm" @created="onPatientCreated" />
    <form id="consultation-form" @submit.prevent="submit">
      <fieldset :disabled="pending || saved" class="form-fields">
        <section class="card form-section">
          <div class="section-title">
            <span class="section-number">02</span>
            <div>
              <h2>Diagnoses <span class="required">*</span></h2>
              <p>Select one or more relevant ICD-10 codes.</p>
            </div>
          </div>
          <DiagnosisSearch
            :selected="diagnoses"
            selectable
            @select="selectDiagnosis"
          />
          <div v-if="diagnoses.length" class="selected-diagnoses">
            <h3>
              Selected <span class="count-badge">{{ diagnoses.length }}</span>
            </h3>
            <div
              v-for="item in diagnoses"
              :key="item.code"
              class="selected-diagnosis"
            >
              <span class="code-tag">{{ item.code }}</span
              ><span>{{ item.name }}</span
              ><button
                type="button"
                class="icon-button"
                :aria-label="`Remove diagnosis ${item.code}`"
                @click="
                  diagnoses = diagnoses.filter((code) => code.code !== item.code)
                "
              >
                <AppIcon name="close" />
              </button>
            </div>
          </div>
        </section>
        <section class="card form-section">
          <div class="section-title">
            <span class="section-number">03</span>
            <div>
              <h2>Treatment notes</h2>
              <p>Document symptoms, assessment, and the treatment plan.</p>
            </div>
          </div>
          <label for="notes"
            >Consultation notes <span class="required">*</span></label
          ><textarea
            id="notes"
            v-model="notes"
            required
            maxlength="10000"
            rows="7"
            placeholder="Symptoms and history…&#10;Clinical assessment…&#10;Treatment plan and follow-up…"
          />
          <div class="field-hint">
            <span>Review the details before saving this record.</span
            ><span>{{ notes.length.toLocaleString('en-GB') }} / 10,000</span>
          </div>
        </section>
      </fieldset>
      <div v-if="error" class="notice error" role="alert">{{ error }}</div>
      <div class="form-actions">
        <span class="muted"><span class="required">*</span> Required fields</span>
        <div>
          <NuxtLink to="/consultations" class="button secondary">Cancel</NuxtLink
          ><button class="button primary" :disabled="pending || saved">
            <AppIcon name="check" />{{
              pending
                ? 'Saving…'
                : saved
                  ? 'Consultation saved'
                  : 'Save consultation'
            }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>
