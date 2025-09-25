export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type Recommendation = {
  isbn13: string;
  title: string;
  author?: string | null;
  reason?: string | null;
  ndc?: string | null;
  ndlc?: string | null;
};

export type AvailabilityRow = {
  isbn13: string;
  systemid: string;
  status: string;
  opacUrl?: string | null;
};

export type GoalSummary = {
  id: string;
  title: string;
  description?: string | null;
  due_date?: string | null;
  created_at: string;
  updated_at: string;
  archived: boolean;
  progress: number;
  total_books: number;
  done_books: number;
};

export type GoalDetail = GoalSummary & {
  books: {
    book: Recommendation;
    status: "unread" | "reading" | "done";
    position: number;
    completed_at?: string | null;
  }[];
};

export async function fetchRecommendations(purpose: string): Promise<Recommendation[]> {
  const resp = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ purpose })
  });
  if (!resp.ok) {
    throw new Error("Failed to fetch recommendations");
  }
  return resp.json();
}

export async function fetchAvailability(isbns: string[], city: string): Promise<AvailabilityRow[]> {
  const resp = await fetch(`${API_BASE}/availability`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ isbns, city })
  });
  if (!resp.ok) {
    throw new Error("Failed to fetch availability");
  }
  return resp.json();
}

export async function fetchGoals(token: string): Promise<GoalSummary[]> {
  const resp = await fetch(`${API_BASE}/mypage/goals`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  if (!resp.ok) {
    throw new Error("Failed to fetch goals");
  }
  const data = await resp.json();
  return data.items ?? [];
}

export async function fetchGoalDetail(goalId: string, token: string): Promise<GoalDetail> {
  const resp = await fetch(`${API_BASE}/goals/${goalId}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  if (!resp.ok) {
    throw new Error("Failed to fetch goal detail");
  }
  return resp.json();
}

export async function updateGoalBookStatus(
  goalId: string,
  isbn13: string,
  status: "unread" | "reading" | "done",
  token: string
) {
  const resp = await fetch(`${API_BASE}/goals/${goalId}/books/${isbn13}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ status })
  });
  if (!resp.ok) {
    throw new Error("Failed to update status");
  }
  return resp.json();
}
