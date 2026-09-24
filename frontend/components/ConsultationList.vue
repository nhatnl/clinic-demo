<script setup lang="ts">
import type { Consultation } from '~/types/clinic'
const props = defineProps<{ search?: boolean }>()
const route = useRoute()
const router = useRouter()
const patient = ref(String(route.query.patient || ''))
const diagnosis = ref(String(route.query.diagnosis_code || ''))
const page = ref(1)
const expanded = ref<string | number | null>(null)
const query = computed(() =>
  props.search
    ? {
        ...(route.query.patient ? { patient: String(route.query.patient) } : {}),
        ...(route.query.diagnosis_code
          ? { diagnosis_code: String(route.query.diagnosis_code) }
          : {}),
      }
    : {},
)
const { data, status, error, refresh } = await useFetch<Consultation[]>(
  '/api/consultation',
  { query, default: () => [] },
)
// ponytail: paginate the returned list locally; add API pagination when record volume grows.
const pageSize = 10
const pages = computed(() =>
  Math.max(1, Math.ceil(data.value.length / pageSize)),
)
const rows = computed(() =>
  data.value.slice((page.value - 1) * pageSize, page.value * pageSize),
)
const applied = computed(() =>
  Boolean(query.value.patient || query.value.diagnosis_code),
)
watch(page, () => {
  expanded.value = null
})
watch(query, () => {
  page.value = 1
  expanded.value = null
})
watch(pages, (count) => {
  page.value = Math.min(page.value, count)
})
watch(
  () => route.query,
  (value) => {
    patient.value = String(value.patient || '')
    diagnosis.value = String(value.diagnosis_code || '')
  },
)
async function searchNotes() {
  await router.replace({
    query: {
      ...(patient.value.trim() ? { patient: patient.value.trim() } : {}),
      ...(diagnosis.value.trim()
        ? { diagnosis_code: diagnosis.value.trim().toUpperCase() }
        : {}),
    },
  })
}
function date(value: string) {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime())
    ? '—'
    : new Intl.DateTimeFormat('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        timeZone: 'Asia/Ho_Chi_Minh',
      }).format(parsed)
}
const todayCount = computed(
  () =>
    data.value.filter(
      (item) => date(item.created_at) === date(new Date().toISOString()),
    ).length,
)
</script>

<template>
  <div class="page-heading">
    <div>
      <span class="eyebrow">PATIENT RECORDS</span>
      <h1>
        {{ search ? 'Search records' : 'Consultations'
        }}<span class="heading-dot">.</span>
      </h1>
      <p>
        {{
          search
            ? 'Find a consultation by patient name or diagnosis code.'
            : 'A clear view of every visit. A better continuity of care.'
        }}
      </p>
    </div>
    <NuxtLink to="/consultations/new" class="button primary"
      ><AppIcon name="plus" />New consultation</NuxtLink
    >
  </div>
  <form v-if="search" class="card search-form" @submit.prevent="searchNotes">
    <div class="field">
      <label for="patient-search">Patient name</label
      ><input
        id="patient-search"
        v-model="patient"
        type="search"
        maxlength="50"
        placeholder="Search by patient name…"
      />
    </div>
    <div class="field">
      <label for="code-search">ICD-10 diagnosis code</label
      ><input
        id="code-search"
        v-model="diagnosis"
        type="search"
        maxlength="8"
        placeholder="e.g. A00.0"
      />
    </div>
    <button class="button primary" :disabled="status === 'pending'">
      <AppIcon name="search" />Search</button
    ><NuxtLink v-if="applied" to="/search" class="button secondary"
      >Clear filters</NuxtLink
    >
  </form>
  <div v-else class="stats-grid">
    <div class="stat-card">
      <div>
        <span>Total consultations</span
        ><strong>{{ error || status === 'pending' ? '—' : data.length }}</strong
        ><small>Recorded consultations</small>
      </div>
      <span class="stat-icon"><AppIcon name="file" /></span>
    </div>
    <div class="stat-card">
      <div>
        <span>Today’s consultations</span
        ><strong>{{ error || status === 'pending' ? '—' : todayCount }}</strong
        ><small>Clinic time · UTC+7</small>
      </div>
      <span class="stat-icon warm"><AppIcon name="users" /></span>
    </div>
    <NuxtLink to="/diagnoses" class="stat-card directory-card"
      ><div>
        <span>Diagnosis reference</span><strong>ICD-10</strong
        ><small>Browse codes and descriptions</small>
      </div>
      <AppIcon name="arrow"
    /></NuxtLink>
  </div>
  <div
    v-if="!search && route.query.created === '1'"
    class="notice success"
    role="status"
  >
    <AppIcon name="check" />Consultation saved successfully.
  </div>
  <ApiFeedback v-if="error" :error="error" @retry="refresh()" />
  <section class="card records-card" :aria-busy="status === 'pending'">
    <div class="card-heading">
      <div>
        <h2>
          {{ search ? 'Search results' : 'Consultation history'
          }}<span v-if="!error && status !== 'pending'" class="count-badge">{{
            data.length
          }}</span>
        </h2>
        <p>
          {{
            applied
              ? 'Results matching your filters'
              : 'Patient visits and treatment notes, all in one place'
          }}
        </p>
      </div>
      <NuxtLink v-if="!search" to="/search" class="button secondary small"
        ><AppIcon name="search" />Search</NuxtLink
      >
    </div>
    <div v-if="status === 'pending'" class="empty-state" role="status">
      <span class="spinner" />
      <h3>Loading consultations…</h3>
    </div>
    <div v-else-if="error" class="empty-state">
      <span class="empty-icon"><AppIcon name="file" /></span>
      <h3>Records are unavailable</h3>
      <p>Records will appear once the service is connected.</p>
    </div>
    <div v-else-if="!data.length" class="empty-state">
      <span class="empty-icon"
        ><AppIcon :name="search ? 'search' : 'file'"
      /></span>
      <h3>
        {{
          applied
            ? 'No matching consultations'
            : 'Your first consultation starts here'
        }}
      </h3>
      <p>
        {{
          applied
            ? 'Try a different patient name or diagnosis code.'
            : 'Create a consultation to start building your patient records.'
        }}
      </p>
      <NuxtLink v-if="!applied" to="/consultations/new" class="button secondary"
        ><AppIcon name="plus" />New consultation</NuxtLink
      >
    </div>
    <template v-else
      ><div class="table-scroll" tabindex="0" role="region" aria-label="Consultation table, scroll horizontally to see all columns">
        <table>
          <caption class="sr-only">
            Consultations and treatment notes
          </caption>
          <thead>
            <tr>
              <th>PATIENT</th>
              <th>VISIT DATE</th>
              <th>DIAGNOSIS</th>
              <th>TREATMENT NOTES</th>
              <th><span class="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="item in rows" :key="item.id"
              ><tr>
                <td>
                  <div class="patient-cell">
                    <span class="patient-avatar">{{
                      item.patient.name.slice(0, 1).toUpperCase()
                    }}</span>
                    <div>
                      <strong>{{ item.patient.name }}</strong
                      ><small
                        >{{ item.patient.age }} years · Patient #{{ item.patient.id }}</small
                      >
                    </div>
                  </div>
                </td>
                <td class="nowrap">{{ date(item.created_at) }}</td>
                <td>
                  <div class="code-list">
                    <span
                      v-for="code in item.diagnoses"
                      :key="code.code"
                      class="code-tag"
                      :title="code.name"
                      >{{ code.code }}</span
                    >
                  </div>
                </td>
                <td>
                  <p class="note-preview">{{ item.note }}</p>
                </td>
                <td>
                  <button
                    class="text-button nowrap"
                    :aria-expanded="expanded === item.id"
                    :aria-controls="`note-${item.id}`"
                    @click="expanded = expanded === item.id ? null : item.id"
                  >
                    {{ expanded === item.id ? 'Close' : 'Details' }}
                  </button>
                </td>
              </tr>
              <tr
                v-if="expanded === item.id"
                :id="`note-${item.id}`"
                class="detail-row"
              >
                <td colspan="5">
                  <div class="consultation-detail">
                    <div>
                      <h3>Diagnoses</h3>
                      <p v-for="code in item.diagnoses" :key="code.code">
                        <span class="code-tag">{{ code.code }}</span>
                        {{ code.name }}
                      </p>
                    </div>
                    <div>
                      <h3>Treatment notes</h3>
                      <p class="full-note">{{ item.note }}</p>
                      <NuxtLink :to="`/consultations/new?patient_id=${item.patient.id}`" class="text-button">New consultation for this patient</NuxtLink>
                    </div>
                  </div>
                </td>
              </tr></template
            >
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span
          >Showing {{ (page - 1) * pageSize + 1 }}–{{
            Math.min(page * pageSize, data.length)
          }}
          of {{ data.length }} consultations</span
        >
        <div class="pagination">
          <button
            class="button secondary small"
            :disabled="page <= 1"
            @click="page--"
          >
            Previous</button
          ><span>{{ page }} / {{ pages }}</span
          ><button
            class="button secondary small"
            :disabled="page >= pages"
            @click="page++"
          >
            Next
          </button>
        </div>
      </div></template
    >
  </section>
  <p class="page-note">
    <AppIcon name="shield" />Patient information is for authorized care purposes
    only.
  </p>
</template>
