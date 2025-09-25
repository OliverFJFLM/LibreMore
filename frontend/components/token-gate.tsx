"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "libremore-token";

export function useAuthToken(): [string | null, (token: string | null) => void] {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
    if (stored) {
      setToken(stored);
    }
  }, []);

  const update = (value: string | null) => {
    if (typeof window === "undefined") return;
    if (value) {
      localStorage.setItem(STORAGE_KEY, value);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
    setToken(value);
  };

  return [token, update];
}

export default function TokenGate({ onToken }: { onToken: (token: string) => void }) {
  const [token, setToken] = useAuthToken();
  const [input, setInput] = useState("");

  useEffect(() => {
    if (token) {
      onToken(token);
    }
  }, [token, onToken]);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setToken(input);
    onToken(input);
  };

  if (token) {
    return (
      <div className="flex items-center justify-between rounded-md border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600">
        <span>認証済み</span>
        <button className="text-indigo-600" onClick={() => setToken(null)}>
          ログアウト
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 rounded-md border border-slate-200 bg-white p-4 text-sm">
      <label className="font-medium">APIトークン</label>
      <input
        type="password"
        value={input}
        onChange={(event) => setInput(event.target.value)}
        className="rounded-md border border-slate-300 px-2 py-1"
        placeholder="バックエンドで発行したJWTを貼り付け"
      />
      <button type="submit" className="self-start rounded-md bg-indigo-600 px-3 py-1 text-white">
        保存
      </button>
    </form>
  );
}
