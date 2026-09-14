const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  const contentType = response.headers.get("content-type") ?? "";

  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
        ? data.detail
        : "Request failed.";

    throw new Error(message);
  }

  return data as T;
}


export interface LoginRequest {
  organization_slug: string
  email: string
  password: string
}

export interface AuthenticatedUser {
  id: string
  organization_id: string
  email: string
  first_name: string
  last_name: string | null
  phone: string | null
  role: string
  status: string
  is_email_verified: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: AuthenticatedUser
}

export async function login(
  payload: LoginRequest,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}


export interface Lead {
  id: string
  organization_id: string
  title: string
  first_name: string | null
  last_name: string | null
  email: string | null
  phone: string | null
  job_title: string | null
  company_name: string | null
  source: string | null
  status: string
  estimated_value: string | null
  currency: string
  description: string | null
  created_at: string
  updated_at: string
}

export interface LeadListResponse {
  items: Lead[]
  total: number
  limit: number
  offset: number
}

export async function getLeads(
  accessToken: string,
  limit = 20,
  offset = 0,
): Promise<LeadListResponse> {
  return apiRequest<LeadListResponse>(
    `/leads?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  )
}


const ACCESS_TOKEN_KEY = 'nivag_access_token'

export function saveAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function clearAccessToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
}