"use client";

import { useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import { AvailabilityRow, fetchAvailability, Recommendation } from "../lib/api";
import { useEffect, useMemo, useState } from "react";

const STATUS_PRIORITY: Record<string, number> = {
  "在架": 1,
  "貸出中": 2,
  "予約受付中": 3
};

function AvailabilityBadge({ rows }: { rows: AvailabilityRow[] | undefined }) {
  if (!rows || rows.length === 0) {
    return <span className="text-sm text-slate-500">照会中...</span>;
  }
  const best = [...rows].sort((a, b) => (STATUS_PRIORITY[a.status] ?? 4) - (STATUS_PRIORITY[b.status] ?? 4))[0];
  return (
    <span className={clsx("rounded-md px-2 py-1 text-sm", best.status === "在架" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800")}>{
      best.status
    }</span>
  );
}

export default function BookCard({ recommendation, city }: { recommendation: Recommendation; city: string }) {
  const [isbns] = useState([recommendation.isbn13]);
  const { data } = useQuery({
    queryKey: ["availability", recommendation.isbn13],
    queryFn: () => fetchAvailability(isbns, city),
    staleTime: 1000 * 60 * 5
  });
  const opacUrl = data?.find((row) => row.opacUrl)?.opacUrl;
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-1">
        <h3 className="text-lg font-semibold">{recommendation.title}</h3>
        {recommendation.author && <p className="text-sm text-slate-600">{recommendation.author}</p>}
        {recommendation.reason && <p className="text-sm text-slate-500">{recommendation.reason}</p>}
      </div>
      <div className="flex items-center justify-between">
        <AvailabilityBadge rows={data} />
        {opacUrl && (
          <a
            href={opacUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded-md bg-indigo-600 px-3 py-1 text-sm font-medium text-white hover:bg-indigo-500"
          >
            OPACで確認
          </a>
        )}
      </div>
    </div>
  );
}
