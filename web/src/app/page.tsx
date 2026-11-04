
"use client";

import { useState } from "react";

const sections = [
  { icon: "🎬", title: "I miei progetti", description: "Crea e organizza i tuoi videoclip." },
  { icon: "👥", title: "Personaggi", description: "Gestisci fotografie e caratteristiche." },
  { icon: "📝", title: "Storyboard", description: "Organizza e modifica le scene." },
  { icon: "🎞️", title: "Produzione video", description: "Genera immagini, animazioni e montaggi." },
];

export default function Home() {
  const [selected, setSelected] = useState("I miei progetti");

  return (
    <main className="min-h-screen bg-[#10111b] px-5 py-8 text-white">
      <div className="mx-auto max-w-5xl">
        <header className="mb-10 flex items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="text-3xl text-violet-400">▶</span>
              <h1 className="text-4xl font-bold tracking-tight">NAMI</h1>
            </div>
            <p className="ml-11 text-sm tracking-[0.2em] text-violet-300">
              storie su misura
            </p>
          </div>
          <span className="rounded-full border border-violet-400/30 px-3 py-2 text-xs text-violet-200">
            Studio 2.0
          </span>
        </header>

        <section className="mb-8 rounded-3xl border border-white/10 bg-gradient-to-br from-violet-900/60 to-[#1c1d2d] p-7">
          <p className="mb-2 text-sm text-violet-200">Il tuo studio creativo</p>
          <h2 className="mb-3 text-3xl font-semibold">
            Trasforma una canzone in una storia.
          </h2>
          <p className="max-w-xl text-sm leading-6 text-slate-300">
            Organizza personaggi, storyboard e produzione dei tuoi videoclip
            personalizzati, mantenendo il controllo di ogni scena.
          </p>
          <button
            onClick={() => setSelected("I miei progetti")}
            className="mt-6 rounded-xl bg-violet-500 px-5 py-3 font-semibold text-white hover:bg-violet-400"
          >
            + Nuovo progetto
          </button>
        </section>

        <h3 className="mb-4 text-lg font-semibold">Il tuo spazio di lavoro</h3>

        <div className="grid gap-4 sm:grid-cols-2">
          {sections.map((section) => (
            <button
              key={section.title}
              onClick={() => setSelected(section.title)}
              className={`rounded-2xl border p-6 text-left transition ${
                selected === section.title
                  ? "border-violet-400 bg-violet-500/20"
                  : "border-white/10 bg-[#1c1e2d] hover:border-violet-400/50"
              }`}
            >
              <span className="text-3xl">{section.icon}</span>
              <h4 className="mt-4 text-xl font-semibold">{section.title}</h4>
              <p className="mt-2 text-sm text-slate-400">
                {section.description}
              </p>
            </button>
          ))}
        </div>

        <section className="mt-8 rounded-2xl border border-white/10 bg-[#1c1e2d] p-6">
          <p className="mb-2 text-xs uppercase tracking-widest text-violet-300">
            Sezione selezionata
          </p>
          <h3 className="text-xl font-semibold">{selected}</h3>
          <p className="mt-2 text-sm text-slate-400">
            Questa sezione verrà sviluppata nei prossimi passaggi.
            Per ora nessuna generazione AI viene eseguita.
          </p>
        </section>

        <footer className="mt-10 text-center text-xs text-slate-500">
          NAMI Studio — Storie su misura
        </footer>
      </div>
    </main>
  );
}
