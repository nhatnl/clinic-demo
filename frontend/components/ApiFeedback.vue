<script setup lang="ts">
const props = defineProps<{ error: unknown }>()
const isUnauthorized = computed(() => {
  const error = props.error as { status?: number; statusCode?: number } | null
  return error?.status === 401 || error?.statusCode === 401
})
defineEmits<{ retry: [] }>()
</script>
<template>
  <div class="notice error" role="alert">
    <div>
      <strong>Unable to complete your request</strong>
      <p>{{ errorMessage(error) }}</p>
    </div>
    <div class="notice-actions">
      <NuxtLink
        v-if="isUnauthorized"
        to="/login"
        class="button secondary small"
        >Sign in again</NuxtLink
      ><button
        v-else
        type="button"
        class="button secondary small"
        @click="$emit('retry')"
      >
        Try again
      </button>
    </div>
  </div>
</template>
