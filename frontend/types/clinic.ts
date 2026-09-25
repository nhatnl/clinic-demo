export interface Session {
  id: string
  role: number
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Diagnosis {
  code: string
  name: string
  description?: string | null
  is_valid_for_submission?: boolean
}

export interface Patient {
  id: number
  name: string
  age: number
}

export interface PatientRecord {
  id: number
  first_name: string
  last_name: string
  age: number
  gender: string
}

export interface ConsultationCreator {
  id: number
  email: string
  first_name?: string | null
  last_name?: string | null
  role: number
}

export interface Consultation {
  id: number
  patient: Patient
  created_by: ConsultationCreator
  note: string
  diagnoses: Diagnosis[]
  created_at: string
  updated_at: string
}
