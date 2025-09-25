"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useCallback, useState } from "react";
import TokenGate from "../../components/token-gate";
import { GoalSummary, fetchGoals } from "../../lib/api";

export default function MyPage() {
  const [token, setToken] = useState<string | null>(null);
  const query = useQuery<GoalSummary[]>({
    queryKey: ["goals", token],
    queryFn: () => fetchGoals(token ?? ""),
    enabled: Boolean(token)
  });

  const handleToken = useCallback((next: string) => {
    setToken(next);
  }, []);

  return (
    <div className="flex flex-col gap-4">
      <TokenGate onToken={handleToken} />
      {!token && <p className="text-sm text-slate-600">トークンを入力すると目的一覧が表示されます。</p>}
      {token && (
        <div className="flex flex-col gap-3">
          <h2 className="text-xl font-semibold">目的一覧</h2>
          {query.isLoading && <p className="text-sm text-slate-600">読み込み中...</p>}
          {query.data?.map((goal) => (
            <Link key={goal.id} href={`/goals/${goal.id}`} className="rounded-md border border-slate-200 bg-white p-4">
              <div className="flex flex-col gap-1">
                <span className="text-lg font-semibold">{goal.title}</span>
                <span className="text-sm text-slate-600">
                  進捗: {goal.done_books}/{goal.total_books}冊 ({Math.round(goal.progress * 100)}%)
                </span>
              </div>
            </Link>
          ))}
          {query.data && query.data.length === 0 && (
            <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-500">
              まだ目的が登録されていません。
            </p>
          )}
        </div>
      )}
    </div>
  );
}
