const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'


async function parseResponse(response, fallbackMessage) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null)

    throw new Error(
      errorData?.detail ||
        fallbackMessage ||
        `Request failed with HTTP ${response.status}`
    )
  }

  return response.json()
}


export async function checkBackend() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  )

  return parseResponse(
    response,
    'Backend health check failed'
  )
}


export async function getDocuments() {
  const response = await fetch(
    `${API_BASE_URL}/documents/`
  )

  return parseResponse(
    response,
    'Failed to load documents'
  )
}


export async function uploadDocument(file) {
  if (!file) {
    throw new Error('No document selected')
  }

  const formData = new FormData()

  formData.append('file', file)

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: 'POST',
      body: formData,
    }
  )

  return parseResponse(
    response,
    'Document upload failed'
  )
}


export async function searchPapers(
  query,
  { signal } = {}
) {
  const trimmedQuery = query.trim()

  if (!trimmedQuery) {
    return {
      papers: [],
    }
  }

  const response = await fetch(
    `${API_BASE_URL}/papers/search?q=${encodeURIComponent(
      trimmedQuery
    )}`,
    {
      signal,
    }
  )

  return parseResponse(
    response,
    'Paper search failed'
  )
}


export async function getPaperExplanation(
  documentId
) {
  if (!documentId) {
    throw new Error(
      'A document must be selected before requesting an explanation'
    )
  }

  const response = await fetch(
    `${API_BASE_URL}/api/documents/${documentId}/explanation`
  )

  return parseResponse(
    response,
    'Failed to generate paper explanation'
  )
}


export async function chatWithDocument(
  documentId,
  question
) {
  if (!documentId) {
    throw new Error(
      'A document must be selected before asking a question'
    )
  }

  const trimmedQuestion = question.trim()

  if (!trimmedQuestion) {
    throw new Error(
      'Question cannot be empty'
    )
  }

  const response = await fetch(
    `${API_BASE_URL}/api/chat`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document_id: Number(documentId),
        question: trimmedQuestion,
      }),
    }
  )

  return parseResponse(
    response,
    'Failed to get an answer from ResearchPilot'
  )
}


export { API_BASE_URL }