<script setup lang="ts">
import type { Diagnosis } from '~/types/clinic'
const props = withDefaults(
  defineProps<{ selected?: Diagnosis[]; selectable?: boolean }>(),
  { selected: () => [], selectable: false },
)
const emit = defineEmits<{ select: [diagnosis: Diagnosis] }>()
const term = ref('')
const results = ref<Diagnosis[]>([])
const pending = ref(false)
const searched = ref(false)
const error = ref<unknown>(null)
let controller: AbortController | undefined
async function search() {
  controller?.abort()
  const current = new AbortController()
  controller = current
  if (!term.value.trim()) {
    results.value = []
    searched.value = false
    pending.value = false
    error.value = null
    return
  }
  pending.value = true
  error.value = null
  searched.value = true
  try {
    results.value = await $fetch<Diagnosis[]>('/api/diagnosis', {
      query: { search: term.value.trim() },
      signal: current.signal,
    })
  } catch (cause) {
    if (!current.signal.aborted) {
      error.value = cause
      results.value = []
    }
  } finally {
    if (!current.signal.aborted) pending.value = false
  }
}
onBeforeUnmount(() => controller?.abort())
const isSelected = (code: string) =>
  props.selected.some((item) => item.code === code)
</script>

<template>
  <div class="diagnosis-search">
    <label for="diagnosis-term">Search by code or diagnosis name</label>
    <div class="search-input-row">
      <div class="input-with-icon">
        <AppIcon name="search" /><input
          id="diagnosis-term"
          v-model="term"
          type="search"
          maxlength="100"
          placeholder="e.g. A00 or Cholera"
          @keydown.enter.prevent="search"
        />
      </div>
      <button
        class="button secondary"
        type="button"
        :disabled="pending || !term.trim()"
        @click="search"
      >
        {{ pending ? 'Searching…' : 'Search' }}
      </button>
    </div>
    <ApiFeedback v-if="error" :error="error" @retry="search" />
    <p v-else-if="pending" class="muted search-hint" role="status">
      Searching diagnosis codes…
    </p>
    <div v-else-if="results.length" class="diagnosis-results">
      <p class="search-hint muted" role="status">
        {{ results.length }} results · Descriptions from the original code
        directory
      </p>
      <ul>
        <li v-for="item in results" :key="item.code">
          <div>
            <span class="code-tag">{{ item.code }}</span
            ><strong>{{ item.name }}</strong
            ><small v-if="item.description && item.description !== item.name">{{
              item.description
            }}</small
            ><small v-if="!item.is_valid_for_submission" class="muted"
              >Category code — select a billable code for the
              consultation</small
            >
          </div>
          <button
            v-if="selectable"
            type="button"
            class="button secondary small"
            :disabled="isSelected(item.code) || !item.is_valid_for_submission"
            :aria-label="`${isSelected(item.code) ? 'Selected' : 'Select'} ${item.code}`"
            @click="emit('select', item)"
          >
            <AppIcon :name="isSelected(item.code) ? 'check' : 'plus'" />{{
              isSelected(item.code) ? 'Selected' : 'Select'
            }}</button
          ><span
            v-else
            class="status-tag"
            :class="{ neutral: !item.is_valid_for_submission }"
            >{{
              item.is_valid_for_submission ? 'Billable code' : 'Category'
            }}</span
          >
        </li>
      </ul>
    </div>
    <p v-else-if="searched" class="search-hint muted" role="status">
      No diagnoses found. Try another code or keyword.
    </p>
    <p v-else class="search-hint muted">
      Enter a keyword, then select Search or press Enter.
    </p>
  </div>
</template>
