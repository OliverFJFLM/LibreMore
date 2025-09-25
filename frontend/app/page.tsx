"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import BookCard from "../components/book-card";
import { fetchRecommendations } from "../lib/api";

export default function HomePage() {
  const [purpose, setPurpose] = useState("");
  const [city, setCity] = useState("宮崎市");
  const [submitted, setSubmitted] = useState<string | null>(null);
  const { data, mutateAsync, isPending } = useMutation({
    mutationFn: (input: string) => fetchRecommendations(input)
  });

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitted(purpose);
    await mutateAsync(purpose);
  };

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <label className="text-sm font-medium" htmlFor="purpose">
          読書の目的を入力
        </label>
        <textarea
          id="purpose"
          className="min-h-[120px] rounded-md border border-slate-300 p-3"
          placeholder="例: キャリアアップのためにデータ分析を学びたい"
          value={purpose}
          onChange={(event) => setPurpose(event.target.value)}
          required
        />
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <span>エリア:</span>
          <input
            value={city}
            onChange={(event) => setCity(event.target.value)}
            className="rounded-md border border-slate-300 px-2 py-1"
          />
        </div>
        <button
          type="submit"
          className="self-start rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500"
          disabled={isPending}
        >
          {isPending ? "分析中..." : "推薦を作成"}
        </button>
      </form>

      {submitted && (
        <section className="flex flex-col gap-4">
          <div>
            <h2 className="text-xl font-semibold">推薦結果</h2>
            <p className="text-sm text-slate-600">目的: {submitted}</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {data?.map((rec) => <BookCard key={rec.isbn13} recommendation={rec} city={city} />)}
            {!data?.length && (
              <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                推薦結果がまだありません。目的を入力して推薦を生成してください。
              </p>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
