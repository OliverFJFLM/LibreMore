"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useCallback } from "react";
import TokenGate, { useAuthToken } from "../../../components/token-gate";
import { GoalDetail, fetchGoalDetail, updateGoalBookStatus } from "../../../lib/api";

export default function GoalDetailPage() {
  const params = useParams();
  const goalId = params?.id as string;
  const [token, setToken] = useAuthToken();
  const queryClient = useQueryClient();

  const query = useQuery<GoalDetail>({
    queryKey: ["goal", goalId, token],
    queryFn: () => fetchGoalDetail(goalId, token ?? ""),
    enabled: Boolean(token)
  });

  const mutation = useMutation({
    mutationFn: ({ isbn13, status }: { isbn13: string; status: "unread" | "reading" | "done" }) =>
      updateGoalBookStatus(goalId, isbn13, status, token ?? ""),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goal", goalId, token] });
    }
  });

  const handleToken = useCallback((next: string) => {
    setToken(next);
  }, [setToken]);

  return (
    <div className="flex flex-col gap-4">
      <TokenGate onToken={handleToken} />
      {!token && <p className="text-sm text-slate-600">トークンを入力すると目的詳細を表示します。</p>}
      {token && query.data && (
        <div className="flex flex-col gap-4">
          <div className="rounded-md border border-slate-200 bg-white p-4">
            <h2 className="text-2xl font-semibold">{query.data.title}</h2>
            {query.data.description && <p className="mt-2 text-sm text-slate-600">{query.data.description}</p>}
            <p className="mt-2 text-sm text-slate-600">
              進捗: {query.data.done_books}/{query.data.total_books}冊 ({Math.round(query.data.progress * 100)}%)
            </p>
          </div>
          <div className="flex flex-col gap-2">
            {query.data.books.map((item) => (
              <div key={item.book.isbn13} className="flex flex-col gap-2 rounded-md border border-slate-200 bg-white p-4">
                <div>
                  <p className="text-lg font-semibold">{item.book.title}</p>
                  <p className="text-sm text-slate-600">{item.book.author}</p>
                </div>
                <div className="flex flex-wrap gap-2 text-sm">
                  {["unread", "reading", "done"].map((status) => (
                    <button
                      key={status}
                      onClick={() => mutation.mutate({ isbn13: item.book.isbn13, status: status as typeof item.status })}
                      className={`rounded-md px-3 py-1 ${item.status === status ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-700"}`}
                    >
                      {status === "unread" ? "未読" : status === "reading" ? "読書中" : "読了"}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
