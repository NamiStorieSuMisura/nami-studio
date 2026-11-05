
"use client";

import { useState } from "react";

const sections = [
  {
    icon: "🎬",
    title: "I miei progetti",
    description: "Crea, gestisci e organizza i tuoi videoclip.",
  },
  {
    icon: "👥",
    title: "Personaggi",
    description: "Gestisci fotografie, ruoli e caratteristiche.",
  },
  {
    icon: "🎞️",
    title: "Scene e storyboard",
    description: "Pianifica, modifica e controlla ogni scena.",
  },
  {
    icon: "📁",
    title: "Archivio e backup",
    description: "Versioni, recupero e progetti eliminati.",
  },
];

export default function Home() {
  const [selected, setSelected] = useState("I miei progetti");

  return (
    <main className="min-h-screen bg-[#0c0b1b] px-4 py-7 text-white sm:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-9 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-fuchsia-400 bg-gradient-to-br from-blue-500 via-violet-600 to-fuchsia-500 text-3xl shadow-[0_0_28px_#a855f766]">
              ▶
            </div>
            <div>
              <h1 className="text-4xl font-black tracking-[0.08em] sm:text-5xl">
                NAMI
              </h1>
              <p className="text-sm tracking-[0.15em] text-fuchsia-200">
                storie su misura
              </p>
            </div>
          </div>

          <span className="rounded-full border border-fuchsia-400/60 bg-violet-900/30 px-4 py-2 text-sm font-semibold">
            ▶ Studio 2.0
          </span>
        </header>

        <section className="relative overflow-hidden rounded-[30px] border border-fuchsia-400/40 bg-gradient-to-br from-[#52206f] via-[#27184d] to-[#111a42] p-7 shadow-[0_0_45px_#7c3aed22] sm:p-10">
          <div className="pointer-events-none absolute -right-16 -top-20 h-64 w-64 rounded-full bg-fuchsia-500/20 blur-3xl" />
          <div className="pointer-events-none absolute bottom-0 right-10 h-40 w-64 rounded-full bg-blue-500/20 blur-3xl" />

          <div className="relative">
            <p className="mb-3 text-sm font-semibold text-fuchsia-200">
              ▶ Il tuo studio creativo
            </p>

            <h2 className="max-w-3xl text-3xl font-extrabold leading-tight sm:text-5xl">
              Trasforma una canzone in una storia.
            </h2>

            <p className="mt-5 max-w-2xl text-sm leading-7 text-slate-200 sm:text-base">
              Organizza personaggi, storyboard e produzione dei tuoi videoclip
              personalizzati, mantenendo il controllo di ogni scena.
            </p>

            <button
              onClick={() => setSelected("I miei progetti")}
              className="mt-8 rounded-full border border-fuchsia-200 bg-gradient-to-r from-violet-600 to-fuchsia-500 px-7 py-4 text-lg font-bold shadow-[0_0_25px_#d946ef88] transition hover:brightness-125"
            >
              ＋ Nuovo progetto
            </button>
          </div>
        </section>

        <div className="mb-6 mt-10 flex items-center gap-3">
          <div className="h-8 w-1.5 rounded-full bg-fuchsia-400" />
          <h3 className="text-2xl font-bold">Il tuo spazio di lavoro</h3>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {sections.map((section) => (
            <button
              key={section.title}
              onClick={() => setSelected(section.title)}
              className={`flex min-h-36 items-center gap-5 rounded-3xl border p-6 text-left transition hover:border-fuchsia-400 ${
                selected === section.title
                  ? "border-fuchsia-400 bg-gradient-to-r from-violet-900/70 to-[#241b43] shadow-[0_0_20px_#a855f733]"
                  : "border-violet-400/25 bg-[#1d1a36]"
              }`}
            >
              <span className="text-5xl">{section.icon}</span>

              <div className="flex-1">
                <h4 className="text-xl font-bold">{section.title}</h4>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {section.description}
                </p>
              </div>

              <span className="text-2xl text-fuchsia-200">›</span>
            </button>
          ))}
        </div>

        <section className="mt-7 rounded-3xl border border-violet-400/20 bg-[#19162e] p-6">
          <p className="text-xs font-semibold uppercase tracking-widest text-fuchsia-300">
            Sezione selezionata
          </p>
          <h3 className="mt-2 text-xl font-bold">{selected}</h3>
          <p className="mt-2 text-sm text-slate-400">
            Stiamo preparando questa funzione. Nessuna generazione AI
            viene avviata da questa pagina.
          </p>
        </section>

        <footer className="mt-10 text-center text-xs text-slate-500">
          ▶ NAMI — storie su misura
        </footer>
      </div>
    </main>
  );
}
