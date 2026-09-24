export interface Session {
  id: string
  role: number
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

export interface Consultation {
  id: number
  patient: Patient
  note: string
  diagnoses: Diagnosis[]
  created_at: string
  updated_at: string
}
