
"use client";

import { useState } from "react";
import { useEffect } from "react";
import { supabase } from "../../supabaseClient";

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
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [loginEmail, setLoginEmail] = useState("");
const [loginPassword, setLoginPassword] = useState("");
  const [projectName, setProjectName] = useState("");
  const [progettoApertoId, setProgettoApertoId] = useState<number | null>(null);
const [progettiSalvati, setProgettiSalvati] = useState<
  {
    id: number;
    name: string;
    lyrics: string | null;
    audio_path: string | null;
  }[]
>([]);

const [audioFile, setAudioFile] = useState<File | null>(null);;
const [audioPath, setAudioPath] = useState<string | null>(null);
const [audioUrl, setAudioUrl] = useState<string | null>(null);
const [lyrics, setLyrics] = useState("");

useEffect(() => {
  supabase.auth.getUser().then(({ data: { user } }) => {
    setUserEmail(user?.email ?? null);
    if (user) {
  caricaProgetti();
  }
   });
}, []);

const accedi = async () => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: loginEmail.trim(),
    password: loginPassword,
  });

  if (error) {
    alert("Accesso non riuscito: " + error.message);
    return;
  }

  setUserEmail(data.user.email ?? null);
  setLoginPassword("");

  await caricaProgetti();
};

const caricaProgetti = async () => {
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) return;

  const { data, error } = await supabase
    .from("projects")
    .select("id, name, lyrics, audio_path")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  if (error) {
    alert("Errore nel caricamento dei progetti: " + error.message);
    return;
  }

  setProgettiSalvati(data ?? []);
};
async function preparaAscoltoAudio(percorso: string) {
  const { data, error } = await supabase.storage
    .from("nami-audio")
    .createSignedUrl(percorso, 3600);

  if (error || !data) {
    alert(
      "Impossibile recuperare l'MP3: " +
      (error?.message ?? "Errore sconosciuto")
    );
    return;
  }

  setAudioUrl(data.signedUrl);
}
async function caricaAudio(
  file: File,
  userId: string,
  projectId: number
) {
  const percorso = `${userId}/${projectId}/${Date.now()}.mp3`;

  const { error } = await supabase.storage
    .from("nami-audio")
    .upload(percorso, file, {
      contentType: "audio/mpeg",
      upsert: false,
    });

  if (error) {
    throw new Error(error.message);
  }

  return percorso;
}


const salvaProgetto = async () => {
  if (!projectName.trim()) {
    alert("Inserisci il nome del progetto.");
    return;
  }

  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  if (authError || !user) {
    alert("Devi effettuare l'accesso per salvare il progetto.");
    return;
  }

  let idProgetto = progettoApertoId;

  if (idProgetto !== null) {
    const { data, error } = await supabase
      .from("projects")
      .update({
        name: projectName.trim(),
        lyrics: lyrics,
      })
      .eq("id", idProgetto)
      .eq("user_id", user.id)
      .select("id")
      .single();

    if (error || !data) {
      alert("Errore nel salvataggio: " + (error?.message ?? "Progetto non trovato"));
      return;
    }
  } else {
    const { data, error } = await supabase
      .from("projects")
      .insert({
        name: projectName.trim(),
        lyrics: lyrics,
        user_id: user.id,
      })
      .select("id")
      .single();

    if (error || !data) {
      alert("Errore nel salvataggio: " + (error?.message ?? "Creazione non riuscita"));
      return;
    }

    idProgetto = data.id;
    setProgettoApertoId(idProgetto);
  }

  if (audioFile && idProgetto !== null) {
    try {
      const percorso = await caricaAudio(
        audioFile,
        user.id,
        idProgetto
      );

      const { error: erroreAudio } = await supabase
        .from("projects")
        .update({ audio_path: percorso })
        .eq("id", idProgetto)
        .eq("user_id", user.id);

      if (erroreAudio) {
        alert(
          "Progetto salvato, ma non è stato possibile associare l'MP3: " +
          erroreAudio.message
        );
        return;
      }

      setAudioPath(percorso);
      setAudioFile(null);
    } catch (errore) {
      alert(
        "Progetto salvato, ma caricamento MP3 non riuscito: " +
        (errore instanceof Error ? errore.message : "Errore sconosciuto")
      );
      return;
    }
  }

  await caricaProgetti();
  alert("Progetto salvato con successo!");
};


if (!userEmail) {
  return (
    <main className="min-h-screen bg-[#0c0b1b] flex items-center justify-center px-4 text-white">
      <div className="w-full max-w-md rounded-3xl border border-fuchsia-400/30 bg-[#19162e] p-8">
        <h1 className="text-center text-4xl font-black text-fuchsia-300">
          NAMI
        </h1>
        <p className="mb-8 text-center text-sm text-fuchsia-200">
          storie su misura
        </p>

        <h2 className="mb-5 text-xl font-bold">
          Accesso privato
        </h2>

        <input
          type="email"
          placeholder="La tua email"
          value={loginEmail}
          onChange={(e) => setLoginEmail(e.target.value)}
          className="mb-4 w-full rounded-xl bg-[#111025] p-3 text-white"
        />

        <input
          type="password"
          placeholder="Password"
          value={loginPassword}
          onChange={(e) => setLoginPassword(e.target.value)}
          className="mb-5 w-full rounded-xl bg-[#111025] p-3 text-white"
        />

        <button
          type="button"
          onClick={accedi}
          className="w-full rounded-xl bg-fuchsia-600 p-3 font-bold hover:bg-fuchsia-500"
        >
          Accedi a NAMI
        </button>
      </div>
    </main>
  );
}


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
onClick={() => {
  setSelected("I miei progetti");
  const nome = prompt("Come vuoi chiamare il nuovo progetto?");

if (nome && nome.trim()) {
  setProgettoApertoId(null);
  setProjectName(nome.trim());
  setLyrics("");
  setAudioFile(null);
  setAudioPath(null);
  setAudioUrl(null);
}
}}
              className="mt-8 rounded-full border border-fuchsia-200 bg-gradient-to-r from-violet-600 to-fuchsia-500 px-7 py-4 text-lg font-bold shadow-[0_0_25px_#d946ef88] transition hover:brightness-125"
            >
              ＋ Nuovo progetto
            </button>
          </div>
        </section>s

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
{projectName && (
  <section className="mt-7 rounded-3xl border border-fuchsia-400/40 bg-[#19162e] p-6">
    <p className="text-sm font-semibold text-fuchsia-300">
      Il tuo nuovo progetto
    </p>
    
<input
  type="text"
  value={projectName}
  onChange={(e) => setProjectName(e.target.value)}
  placeholder="Nome del progetto"
  className="mt-2 w-full rounded-xl border border-fuchsia-400/30 bg-[#111025] p-3 text-2xl font-bold text-white"
/>

    <p className="mt-3 text-sm text-slate-300">
      Prossimo passo: aggiungere la canzone MP3,
      il testo e i personaggi.
    </p>
 <div className="mt-6 space-y-5">
  <div>
    <label className="mb-2 block font-semibold text-fuchsia-200">
      🎵 Carica la canzone MP3
    </label>
    <input
      type="file"
      accept=".mp3,audio/mpeg"
      onChange={(e) => {
        const file = e.target.files?.[0];
        if (file) {
          setAudioFile(file);
        }
      }}
      className="block w-full rounded-xl border border-fuchsia-400/30 bg-[#111025] p-3 text-sm text-white"
    />
    {audioFile && (
      <p className="mt-2 text-sm text-green-300">
        File selezionato: {audioFile.name}
      </p>
    )}
  </div>

  {!audioFile && audioUrl && (
  <div className="rounded-xl border border-fuchsia-400/30 bg-[#111025] p-4">
    <p className="mb-3 font-semibold text-fuchsia-200">
      🎧 Ascolta la canzone salvata
    </p>
    <audio
      controls
      src={audioUrl}
      className="w-full"
    />
  </div>
)}

{audioFile && (
  <div className="rounded-xl border border-fuchsia-400/30 bg-[#111025] p-4">
    <p className="mb-3 font-semibold text-fuchsia-200">
      🎧 Anteprima della canzone selezionata
    </p>
    <audio
      controls
      src={URL.createObjectURL(audioFile)}
      className="w-full"
    />
  </div>
)}
<div>
    <label className="mb-2 block font-semibold text-fuchsia-200">
      📝 Testo della canzone
    </label>
    <textarea
      value={lyrics}
      onChange={(e) => setLyrics(e.target.value)}
      placeholder="Incolla qui il testo della canzone..."
      rows={7}
      className="w-full rounded-xl border border-fuchsia-400/30 bg-[#111025] p-4 text-white"
    />
  
  </div>

  <button
    type="button"
    onClick={salvaProgetto}
    className="mt-6 rounded-xl bg-fuchsia-600 px-6 py-3 font-bold text-white hover:bg-fuchsia-500"
  >
    💾 Salva progetto
  </button>
</div>
</section>
)}
{selected === "I miei progetti" && (
  <section className="mt-7 rounded-3xl border border-violet-400/20 bg-[#19162e] p-6">
    <h2 className="mb-4 text-xl font-bold text-white">
      📁 Progetti salvati
    </h2>

    {progettiSalvati.length === 0 ? (
      <p className="text-slate-300">
        Nessun progetto caricato.
      </p>
    ) : (
      <div className="space-y-3">
        {progettiSalvati.map((progetto) => (
          <div
            key={progetto.id}
            className="rounded-xl border border-violet-400/20 bg-[#111025] p-4 text-white"
          >
            🎬 {progetto.name}

         {progettoApertoId === progetto.id && (
  <p className="mt-2 text-sm font-semibold text-green-400">
    ✓ Progetto aperto
  </p>
)}  

<button
  type="button"
  onClick={() => {
    setProgettoApertoId(progetto.id);
    setProjectName(progetto.name);
    setLyrics(progetto.lyrics ?? "");
    setAudioPath(progetto.audio_path ?? null);
    setAudioUrl(null);

if (progetto.audio_path) {
  void preparaAscoltoAudio(progetto.audio_path);
}
setAudioFile(null);
  }}
  className="mt-3 rounded-xl bg-fuchsia-600 px-4 py-2 font-bold text-white hover:bg-fuchsia-500"
>
  📂 Apri progetto
</button>

          </div>
        ))}
      </div>
    )}
  </section>
)}
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
