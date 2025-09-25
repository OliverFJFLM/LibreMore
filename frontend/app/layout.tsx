import "../styles/globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";
import Providers from "../components/providers";

export const metadata: Metadata = {
  title: "LibreMore",
  description: "City-wide library recommendation service"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <Providers>
          <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-4 py-10">
            <header className="flex flex-col gap-2">
              <h1 className="text-3xl font-bold">LibreMore</h1>
              <p className="text-sm text-slate-600">
                目的から本を探し、宮崎市内の図書館で今すぐ読める蔵書を案内します。
              </p>
            </header>
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
