<script setup lang="ts">
import type { Diagnosis, Page } from '~/types/clinic'
const props = withDefaults(
  defineProps<{ selected?: Diagnosis[]; selectable?: boolean }>(),
  { selected: () => [], selectable: false },
)
const emit = defineEmits<{ select: [diagnosis: Diagnosis] }>()
const term = ref('')
const pageSize = 20
const results = ref<Page<Diagnosis>>({ items: [], total: 0, page: 1, page_size: pageSize })
const page = ref(1)
const searchedTerm = ref('')
const pages = computed(() => Math.max(1, Math.ceil(results.value.total / results.value.page_size)))
const pending = ref(false)
const searched = ref(false)
const error = ref<unknown>(null)
let controller: AbortController | undefined
async function search(nextPage = 1) {
  controller?.abort()
  const current = new AbortController()
  controller = current
  if (nextPage === 1) searchedTerm.value = term.value.trim()
  if (!searchedTerm.value) {
    results.value = { items: [], total: 0, page: 1, page_size: pageSize }
    searched.value = false
    pending.value = false
    error.value = null
    return
  }
  pending.value = true
  page.value = nextPage
  error.value = null
  searched.value = true
  try {
    results.value = await $fetch<Page<Diagnosis>>('/api/diagnosis', {
      query: { search: searchedTerm.value, page: nextPage, page_size: pageSize },
      signal: current.signal,
    })
  } catch (cause) {
    if (!current.signal.aborted) {
      error.value = cause
      results.value = { items: [], total: 0, page: nextPage, page_size: pageSize }
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
          @keydown.enter.prevent="search()"
        />
      </div>
      <button
        class="button secondary"
        type="button"
        :disabled="pending || !term.trim()"
        @click="search()"
      >
        {{ pending ? 'Searching…' : 'Search' }}
      </button>
    </div>
    <ApiFeedback v-if="error" :error="error" @retry="search(page)" />
    <p v-else-if="pending" class="muted search-hint" role="status">
      Searching diagnosis codes…
    </p>
    <div v-else-if="results.items.length" class="diagnosis-results">
      <p class="search-hint muted" role="status">
        {{ results.total }} results · Descriptions from the original code
        directory
      </p>
      <ul>
        <li v-for="item in results.items" :key="item.code">
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
      <div class="table-footer">
        <span>Showing {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, results.total) }} of {{ results.total }}</span>
        <div class="pagination">
          <button type="button" class="button secondary small" :disabled="page <= 1 || pending" @click="search(page - 1)">Previous</button>
          <span>{{ page }} / {{ pages }}</span>
          <button type="button" class="button secondary small" :disabled="page >= pages || pending" @click="search(page + 1)">Next</button>
        </div>
      </div>
    </div>
    <p v-else-if="searched" class="search-hint muted" role="status">
      No diagnoses found. Try another code or keyword.
    </p>
    <p v-else class="search-hint muted">
      Enter a keyword, then select Search or press Enter.
    </p>
  </div>
</template>
