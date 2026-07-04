import { useState, useEffect, useMemo, useRef, useCallback } from "react";
import { Pencil, Settings, ArrowLeft, X, Eye, FileText, Keyboard } from "lucide-react";
import { marked } from "marked";
import { api, ApiEntry, ApiSearchResult } from "./api";

// ── Markdown config ───────────────────────────────────────────
marked.setOptions({ breaks: true });

// ── Data ─────────────────────────────────────────────────────
//
// WICHTIG: Entry hat bewusst NUR ID, Titel, Inhalt, LastModified, Links -
// keine Tags. Das ist keine Notiz-App mit Metadaten, sondern die
// KIVO-Suchengine: du suchst nach dem Inhalt, nicht nach einem Schlagwort,
// das du selbst vorher vergeben musst.
//
// Alle Daten kommen aus der Python-Engine (search/engine.py) ueber die
// lokale API (webapp/server.py) - dieses Frontend sucht, rankt und
// empfiehlt NICHTS selbst, es fragt nur engine.search(...) usw.

type Entry = ApiEntry;

// ── Logo ─────────────────────────────────────────────────────

function KivoIcon({ size = 32, color = "#111110" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="60 135 185 205" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M65,141.74148l2.28854,-1.79956c2.18344,-1.71793 3.33599,-1.80043 25.18694,-1.80043c17.85579,0 23.63674,-0.14417 25.49865,2.48569c0.98676,1.39396 0.87363,3.56612 0.87363,6.9516l0,5.9632l-5.42794,1.94287c-15.48226,5.54201 -29.18655,18.36736 -35.93666,33.63079c-14.85159,33.58278 7.39105,74.08158 44.78308,81.53866c9.5146,1.89785 18.6603,1.18048 28.96528,-2.2728c4.21644,-1.41241 7.94062,-2.5683 8.27585,-2.5683c0.33522,0 5.29627,5.17028 11.02425,11.48963c5.72873,6.31935 15.49608,16.97849 21.70571,23.68679c22.77532,24.60355 25.6588,27.98457 25.10299,29.43406c-0.47181,1.23004 -3.05373,1.39653 -21.63571,1.39653l-21.09958,0l-9.81615,-10.63908c-32.58996,-35.32247 -42.05689,-45.00582 -43.75912,-44.76177c-1.69467,0.24253 -1.76051,1.02763 -2.18199,25.99932c-0.4003,23.75301 -0.56262,25.89036 -2.08854,27.57519c-1.60349,1.76996 -2.37723,1.82634 -24.90647,1.82634l-23.25274,0l-1.79956,-2.28832c-1.79609,-2.28264 -1.80043,-2.52062 -1.80043,-95.03926zM159.69237,158.06609c-0.014,-0.2675 4.11238,-4.85935 9.16916,-10.20506l9.19299,-9.71955l28.5873,0c27.42952,0 28.6573,0.07035 30.32396,1.73703c2.11238,2.11224 2.12449,2.43445 0.21113,5.33616c-1.93418,2.93297 -45.50752,48.94601 -46.34975,48.94601c-0.34771,0 -2.42414,-3.5808 -4.6156,-7.95727c-4.62468,-9.23764 -12.93459,-18.70176 -21.23237,-24.17775c-2.89482,-1.91076 -5.27357,-3.69294 -5.28681,-3.95957zM108.68881,163.70447c3.64435,-1.73095 8.49606,-3.66077 10.78096,-4.28957c5.70338,-1.5677 19.48323,-1.54859 26.21272,0.03734c22.56987,5.32053 41.82419,29.51393 41.76328,52.47844c-0.02346,8.59102 -2.08173,16.60845 -6.40335,24.93235l-3.9005,7.51345l5.72609,5.9304c5.45859,5.65458 5.87364,5.90732 8.91792,5.42037c3.07871,-0.49262 3.40524,-0.27885 9.20435,6.0091c3.30648,3.58608 15.24069,16.06134 26.52032,27.72389c21.60242,22.33492 23.23693,24.60658 22.09239,30.71065c-0.69126,3.68181 -5.12336,8.89636 -8.9043,10.47601c-6.60501,2.75937 -13.00912,0.78169 -18.24221,-5.63415c-3.49906,-4.29135 -6.30195,-7.35871 -31.30467,-34.27063c-8.71815,-9.38255 -15.85022,-17.44425 -15.85022,-17.91379c0,-0.46993 0.44798,-1.83693 0.99508,-3.03898c0.89293,-1.95763 0.64434,-2.60462 -2.38821,-6.23877c-1.86153,-2.23004 -4.20735,-5.05186 -5.21379,-6.2713l-1.82899,-2.21643l-8.15894,4.09914c-17.08216,8.5827 -33.50635,8.86079 -50.26803,0.85207c-8.03631,-3.84072 -18.96309,-14.41889 -23.16496,-22.42761c-8.53404,-16.26566 -9.07078,-33.12534 -1.55377,-48.82194c4.56925,-9.54146 15.59592,-20.60888 24.96882,-25.06004zM94.76228,194.28743c5.28405,-11.1196 16.50013,-20.32579 28.0677,-23.039c5.35378,-1.25501 14.29251,-1.0935 19.8718,0.35955c7.51875,1.9585 13.25883,5.35022 19.27475,11.39073c18.14951,18.21951 15.84795,47.05236 -4.97921,62.38347c-22.54226,16.59483 -55.0724,5.80441 -64.22483,-21.30464c-1.56766,-4.64133 -1.83603,-7.08288 -1.57114,-14.28344c0.29009,-7.88879 0.61665,-9.31066 3.56093,-15.50667zM130.16107,178.5545c-0.57208,-0.68975 -0.76164,-1.70489 -0.42035,-2.25729c0.76277,-1.23429 7.62999,-0.48301 13.86005,1.51647c20.08936,6.44686 30.37543,30.18322 21.39582,49.37246c-3.34129,7.14077 -9.54941,13.28457 -17.25658,17.07913c-5.54221,2.72797 -6.32995,2.87477 -15.43024,2.87477c-9.05489,0 -9.90885,-0.15626 -15.29706,-2.80969c-3.13887,-1.54484 -7.65497,-4.75673 -10.0356,-7.13737c-4.87936,-4.88007 -10.08089,-14.63531 -9.67446,-18.14573c0.23189,-2.00643 0.61491,-2.27204 2.95211,-2.05071c3.5237,0.33371 4.37386,-0.9213 4.91832,-7.25731c0.5717,-6.64247 3.64171,-12.81238 8.69469,-17.47035c4.56074,-4.20357 6.29665,-5.2013 11.98717,-6.89143c3.29702,-0.97882 4.38859,-1.75634 4.80667,-3.41848c0.30042,-1.1994 0.0787,-2.70565 -0.50057,-3.40447z"
        fill={color}
      />
    </svg>
  );
}

// ── Markdown renderer ─────────────────────────────────────────

function MarkdownContent({ content }: { content: string }) {
  const html = useMemo(() => marked(content) as string, [content]);
  return <div className="prose-kivo" dangerouslySetInnerHTML={{ __html: html }} />;
}

// ── Screens / navigation ───────────────────────────────────────

type Screen =
  | { type: "loading" }
  | { type: "search" }
  | { type: "detail"; entryId: string }
  | { type: "edit"; entryId: string | null }
  | { type: "settings" };

function useKeyboardShortcuts({
  screen,
  navigate,
  searchRef,
  onSave,
}: {
  screen: Screen;
  navigate: (s: Screen) => void;
  searchRef: React.RefObject<HTMLInputElement | null>;
  onSave?: () => void;
}) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const meta = e.metaKey || e.ctrlKey;
      const tag = (e.target as HTMLElement).tagName;
      const isInput = tag === "INPUT" || tag === "TEXTAREA";

      if ((meta && e.key === "k") || (e.key === "/" && !isInput)) {
        e.preventDefault();
        searchRef.current?.focus();
        return;
      }

      if (e.key === "Escape") {
        if (isInput) {
          (e.target as HTMLElement).blur();
          return;
        }
        if (screen.type === "detail" || screen.type === "settings" || screen.type === "edit") {
          navigate({ type: "search" });
        }
        return;
      }

      if (meta && e.key === "n") {
        e.preventDefault();
        navigate({ type: "edit", entryId: null });
        return;
      }

      if (meta && e.key === ",") {
        e.preventDefault();
        navigate({ type: "settings" });
        return;
      }

      if (meta && e.key === "s" && screen.type === "edit") {
        e.preventDefault();
        onSave?.();
        return;
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [screen, navigate, searchRef, onSave]);
}

function useSwipeBack(onBack: () => void, enabled = true) {
  useEffect(() => {
    if (!enabled) return;
    let startX = 0;
    let startY = 0;

    const onTouchStart = (e: TouchEvent) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    };

    const onTouchEnd = (e: TouchEvent) => {
      const dx = e.changedTouches[0].clientX - startX;
      const dy = Math.abs(e.changedTouches[0].clientY - startY);
      if (startX < 40 && dx > 60 && dy < 80) {
        onBack();
      }
    };

    window.addEventListener("touchstart", onTouchStart, { passive: true });
    window.addEventListener("touchend", onTouchEnd, { passive: true });
    return () => {
      window.removeEventListener("touchstart", onTouchStart);
      window.removeEventListener("touchend", onTouchEnd);
    };
  }, [onBack, enabled]);
}

/**
 * Debounced Suche gegen die Engine. Kein Client-Side-Filtern mehr -
 * bei leerer Query kommen die zuletzt geaenderten Eintraege von
 * engine.recent(), sonst das gerankte Ergebnis von engine.search().
 */
function useEngineSearch(query: string) {
  const [results, setResults] = useState<ApiSearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const t = setTimeout(async () => {
      try {
        if (!query.trim()) {
          const recent = await api.recent(5);
          if (!cancelled) setResults(recent.map((entry) => ({ entry, score: 0 })));
        } else {
          const found = await api.search(query);
          if (!cancelled) setResults(found);
        }
      } catch {
        if (!cancelled) setResults([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 150);

    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [query]);

  return { results, loading };
}

// ── Search bar ────────────────────────────────────────────────

const SearchBar = ({
  value,
  onChange,
  large,
  inputRef,
}: {
  value: string;
  onChange: (v: string) => void;
  large?: boolean;
  inputRef?: React.RefObject<HTMLInputElement | null>;
}) => (
  <div className="relative flex items-center">
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Search…"
      className={`w-full bg-transparent border-b border-[#e5e5e2] outline-none text-[#111110] placeholder:text-[#c8c8c4] transition-all focus:border-[#c8c8c4] ${
        large ? "text-[22px] pb-3 pr-8" : "text-[15px] pb-2 pr-7"
      }`}
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    />
    {value && (
      <button
        onClick={() => onChange("")}
        className="absolute right-0 text-[#c8c8c4] hover:text-[#8c8c88] transition-colors p-1"
      >
        <X size={large ? 16 : 13} />
      </button>
    )}
  </div>
);

// ── Fixed nav ─────────────────────────────────────────────────

function FixedNav({ onEdit, onSettings }: { onEdit: () => void; onSettings: () => void }) {
  return (
    <div className="fixed bottom-6 right-5 sm:bottom-8 sm:right-8 flex items-center gap-1 z-50">
      <button
        onClick={onEdit}
        className="group flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#111110]/6 active:bg-[#111110]/10 transition-colors duration-150"
        aria-label="New entry (⌘N)"
      >
        <Pencil size={16} strokeWidth={1.5} className="text-[#111110] group-hover:opacity-60 transition-opacity duration-150" />
      </button>
      <button
        onClick={onSettings}
        className="group flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#111110]/6 active:bg-[#111110]/10 transition-colors duration-150"
        aria-label="Settings (⌘,)"
      >
        <Settings size={16} strokeWidth={1.5} className="text-[#8c8c88] group-hover:text-[#111110] transition-colors duration-150" />
      </button>
    </div>
  );
}

// ── Utilities ─────────────────────────────────────────────────

function firstSentence(text: string): string {
  const stripped = text.replace(/[#*`>_~\[\]]/g, "").trim();
  const m = stripped.match(/^[^.!?]+[.!?]/);
  return m ? m[0].trim() : stripped.slice(0, 100) + "…";
}

// ── Loading screen ────────────────────────────────────────────

function LoadingScreen() {
  const [iconVisible, setIconVisible] = useState(false);
  const [nameVisible, setNameVisible] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setIconVisible(true), 100);
    const t2 = setTimeout(() => setNameVisible(true), 500);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, []);

  return (
    <div className="fixed inset-0 bg-[#fafaf8] flex items-center justify-center">
      <div className="flex items-center gap-4">
        <div style={{ opacity: iconVisible ? 1 : 0, transform: iconVisible ? "scale(1)" : "scale(0.85)", transition: "opacity 0.5s ease, transform 0.5s ease" }}>
          <KivoIcon size={40} color="#111110" />
        </div>
        <div style={{ opacity: nameVisible ? 1 : 0, transform: nameVisible ? "translateX(0)" : "translateX(-12px)", transition: "opacity 0.5s ease, transform 0.5s ease" }}>
          <span className="text-[28px] font-semibold tracking-tight text-[#111110] select-none" style={{ fontFamily: "'DM Sans', sans-serif", letterSpacing: "-0.02em" }}>
            KIVO
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Search screen ─────────────────────────────────────────────

function SearchScreen({
  onSelect,
  onEdit,
  onSettings,
  searchRef,
}: {
  onSelect: (id: string, query: string) => void;
  onEdit: () => void;
  onSettings: () => void;
  searchRef: React.RefObject<HTMLInputElement | null>;
}) {
  const [query, setQuery] = useState("");
  const { results } = useEngineSearch(query);

  return (
    <div className="min-h-screen bg-[#fafaf8] px-5 sm:px-10 md:px-20 lg:px-40">
      <div className="flex items-center gap-3 pt-10 sm:pt-12 pb-12 sm:pb-16">
        <KivoIcon size={22} color="#111110" />
        <span className="text-[15px] font-semibold tracking-tight text-[#111110]" style={{ fontFamily: "'DM Sans', sans-serif", letterSpacing: "-0.01em" }}>
          KIVO
        </span>
      </div>

      <div className="max-w-2xl mx-auto">
        <SearchBar value={query} onChange={setQuery} large inputRef={searchRef} />

        <ul className="mt-8 sm:mt-10 space-y-6 sm:space-y-7">
          {results.length === 0 && (
            <p className="text-[#8c8c88] text-[14px]">No entries found.</p>
          )}
          {results.map(({ entry }) => (
            <li key={entry.id} className="flex items-start gap-3 group">
              <span className="mt-[6px] text-[#c8c8c4] text-[12px] flex-shrink-0 select-none">•</span>
              <button onClick={() => onSelect(entry.id, query)} className="text-left min-h-[44px]">
                <p className="text-[15px] sm:text-[16px] font-semibold text-[#111110] leading-snug group-hover:opacity-50 transition-opacity duration-150">
                  {entry.title}
                </p>
                <p className="text-[13px] text-[#8c8c88] mt-0.5 leading-relaxed">
                  {firstSentence(entry.content)}
                </p>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <FixedNav onEdit={onEdit} onSettings={onSettings} />
    </div>
  );
}

// ── Detail screen ─────────────────────────────────────────────

interface RelatedItem {
  entry: ApiEntry;
  kind: "manual" | "suggested";
  index: number; // fuer die ¹ ² Nummerierung bei manuellen Links
}

function DetailScreen({
  entryId,
  onSelect,
  onBack,
  onEdit,
  onSettings,
  searchRef,
}: {
  entryId: string;
  onSelect: (id: string, query: string) => void;
  onBack: () => void;
  onEdit: () => void;
  onSettings: () => void;
  searchRef: React.RefObject<HTMLInputElement | null>;
}) {
  const [entry, setEntry] = useState<ApiEntry | null>(null);
  const [related, setRelated] = useState<RelatedItem[]>([]);
  const [query, setQuery] = useState("");
  const { results: searchResults } = useEngineSearch(query);

  useSwipeBack(onBack);

  useEffect(() => {
    let cancelled = false;
    setEntry(null);
    setRelated([]);

    (async () => {
      const e = await api.get(entryId);
      if (cancelled) return;
      setEntry(e);

      const links = await api.linksFor(entryId);
      if (cancelled) return;

      let manualIdx = 0;
      const items = await Promise.all(
        links.map(async (link) => {
          const target = await api.get(link.target_id);
          const item: RelatedItem = {
            entry: target,
            kind: link.kind,
            index: link.kind === "manual" ? ++manualIdx : 0,
          };
          return item;
        })
      );
      if (!cancelled) setRelated(items);
    })();

    return () => {
      cancelled = true;
    };
  }, [entryId]);

  if (!entry) {
    return <div className="min-h-screen bg-[#fafaf8]" />;
  }

  return (
    <div className="min-h-screen bg-[#fafaf8] px-5 sm:px-10 md:px-20 lg:px-40">
      <div className="flex items-center gap-3 pt-10 pb-3 max-w-2xl mx-auto">
        <button onClick={onBack} className="flex items-center justify-center w-10 h-10 -ml-2 rounded-full hover:bg-[#111110]/6 active:bg-[#111110]/10 transition-colors text-[#c8c8c4] hover:text-[#111110]" aria-label="Back (Esc)">
          <ArrowLeft size={16} strokeWidth={1.5} />
        </button>
        <div className="flex-1">
          <SearchBar value={query} onChange={setQuery} inputRef={searchRef} />
        </div>
      </div>

      {query.trim() && searchResults.length > 0 && (
        <div className="max-w-2xl mx-auto ml-10 sm:ml-12">
          <ul className="py-3 space-y-3">
            {searchResults.map(({ entry: r }) => (
              <li key={r.id} className="flex items-start gap-3 group">
                <span className="mt-[5px] text-[#c8c8c4] text-[11px] flex-shrink-0 select-none">•</span>
                <button onClick={() => { onSelect(r.id, query); setQuery(""); }} className="text-left min-h-[44px]">
                  <p className="text-[14px] font-semibold text-[#111110] group-hover:opacity-50 transition-opacity">{r.title}</p>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <hr className="border-[#e5e5e2] max-w-2xl mx-auto" />

      <div className="max-w-2xl mx-auto pt-8 sm:pt-10 pb-28">
        <h1 className="text-[24px] sm:text-[28px] font-semibold tracking-tight text-[#111110] leading-tight mb-5" style={{ letterSpacing: "-0.02em" }}>
          {entry.title}
        </h1>

        <MarkdownContent content={entry.content} />

        <hr className="border-[#e5e5e2] mt-14 mb-7" />

        <p className="text-[11px] text-[#8c8c88] uppercase tracking-[0.1em] mb-5" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
          Related
        </p>
        <ul className="space-y-4">
          {related.map((r) => (
            <li key={r.entry.id} className="flex items-start gap-3 group">
              <span className="mt-[3px] text-[#8c8c88] text-[12px] flex-shrink-0 select-none w-4" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                {r.kind === "manual" ? ["¹", "²", "³"][r.index - 1] ?? "·" : "ⓘ"}
              </span>
              <button onClick={() => onSelect(r.entry.id, "")} className="text-left min-h-[44px]">
                <p className="text-[15px] font-semibold text-[#111110] group-hover:opacity-50 transition-opacity duration-150">{r.entry.title}</p>
                <p className="text-[12px] text-[#8c8c88] mt-0.5">{firstSentence(r.entry.content)}</p>
              </button>
            </li>
          ))}
          {related.length === 0 && (
            <p className="text-[13px] text-[#8c8c88]">Keine verwandten Eintraege gefunden.</p>
          )}
        </ul>
      </div>

      <FixedNav onEdit={onEdit} onSettings={onSettings} />
    </div>
  );
}

// ── Edit screen ───────────────────────────────────────────────

function EditScreen({
  entryId,
  onSave,
  onBack,
}: {
  entryId: string | null;
  onSave: () => void;
  onBack: () => void;
}) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [preview, setPreview] = useState(false);
  const [loaded, setLoaded] = useState(entryId === null);

  useSwipeBack(onBack);

  useEffect(() => {
    if (entryId === null) {
      setLoaded(true);
      return;
    }
    (async () => {
      const e = await api.get(entryId);
      setTitle(e.title);
      setContent(e.content);
      setLoaded(true);
    })();
  }, [entryId]);

  const handleSave = useCallback(async () => {
    if (!title.trim()) return;
    if (entryId) {
      await api.update(entryId, title.trim(), content.trim());
    } else {
      await api.create(title.trim(), content.trim());
    }
    onSave();
  }, [title, content, entryId, onSave]);

  useEffect(() => {
    (window as any).__kivoSave = handleSave;
    return () => { delete (window as any).__kivoSave; };
  }, [handleSave]);

  if (!loaded) {
    return <div className="min-h-screen bg-[#fafaf8]" />;
  }

  return (
    <div className="min-h-screen bg-[#fafaf8] px-5 sm:px-10 md:px-20 lg:px-40">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between pt-10 pb-8">
          <button onClick={onBack} className="text-[#8c8c88] hover:text-[#111110] transition-colors text-[14px] min-h-[44px] flex items-center">
            Cancel
          </button>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPreview((p) => !p)}
              className="group flex items-center gap-1.5 text-[13px] text-[#8c8c88] hover:text-[#111110] transition-colors px-2 py-1.5 rounded hover:bg-[#111110]/5 min-h-[44px]"
            >
              {preview
                ? <><FileText size={13} strokeWidth={1.5} /> Edit</>
                : <><Eye size={13} strokeWidth={1.5} /> Preview</>
              }
            </button>
            <button
              onClick={handleSave}
              disabled={!title.trim()}
              className="text-[14px] font-semibold text-[#111110] disabled:opacity-30 hover:opacity-60 transition-opacity min-h-[44px] px-2"
            >
              Save
            </button>
          </div>
        </div>

        {preview ? (
          <div>
            <h1 className="text-[26px] font-semibold tracking-tight text-[#111110] mb-5" style={{ letterSpacing: "-0.02em" }}>
              {title || <span className="text-[#c8c8c4]">Untitled</span>}
            </h1>
            <MarkdownContent content={content || "*Nothing yet…*"} />
          </div>
        ) : (
          <>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Title"
              autoFocus
              className="w-full bg-transparent outline-none text-[24px] sm:text-[26px] font-semibold text-[#111110] placeholder:text-[#c8c8c4] mb-5 min-h-[44px]"
              style={{ letterSpacing: "-0.02em", fontFamily: "'DM Sans', sans-serif" }}
            />
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={"Write in Markdown…\n\n# Heading\n**bold**, *italic*, `code`\n- list item"}
              rows={18}
              className="w-full bg-transparent outline-none text-[15px] sm:text-[16px] text-[#3d3d3a] placeholder:text-[#c8c8c4] leading-[1.75] resize-none"
              style={{ fontFamily: "'DM Sans', sans-serif" }}
            />
          </>
        )}
      </div>
    </div>
  );
}

// ── Settings screen ───────────────────────────────────────────

const SHORTCUTS = [
  { keys: "⌘K / /", action: "Focus search" },
  { keys: "⌘N", action: "New entry" },
  { keys: "⌘S", action: "Save entry" },
  { keys: "⌘,", action: "Settings" },
  { keys: "Esc", action: "Go back" },
];

function SettingsScreen({ onBack }: { onBack: () => void }) {
  useSwipeBack(onBack);
  return (
    <div className="min-h-screen bg-[#fafaf8] px-5 sm:px-10 md:px-20 lg:px-40">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 pt-10 pb-10">
          <button onClick={onBack} className="flex items-center justify-center w-10 h-10 -ml-2 rounded-full hover:bg-[#111110]/6 active:bg-[#111110]/10 transition-colors text-[#c8c8c4] hover:text-[#111110]">
            <ArrowLeft size={16} strokeWidth={1.5} />
          </button>
          <span className="text-[15px] font-semibold text-[#111110]">Settings</span>
        </div>

        <div className="space-y-10">
          {[
            { label: "Account", items: ["Sign out", "Change email", "Change password"] },
            { label: "Appearance", items: ["Light mode", "System default", "Font size"] },
            { label: "Data", items: ["Export all entries", "Import entries", "Delete all data"] },
          ].map((group) => (
            <div key={group.label}>
              <p className="text-[11px] text-[#8c8c88] uppercase tracking-[0.1em] mb-4" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                {group.label}
              </p>
              <ul className="space-y-1">
                {group.items.map((item) => (
                  <li key={item}>
                    <button className="text-[15px] text-[#111110] hover:opacity-50 transition-opacity text-left min-h-[44px] flex items-center w-full">
                      {item}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div>
            <p className="text-[11px] text-[#8c8c88] uppercase tracking-[0.1em] mb-4 flex items-center gap-1.5" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
              <Keyboard size={11} />
              Keyboard shortcuts
            </p>
            <ul className="space-y-3">
              {SHORTCUTS.map((s) => (
                <li key={s.keys} className="flex items-center justify-between min-h-[36px]">
                  <span className="text-[14px] text-[#111110]">{s.action}</span>
                  <span className="text-[12px] text-[#8c8c88] bg-[#f2f2f0] px-2 py-0.5 rounded" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                    {s.keys}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-[11px] text-[#8c8c88] uppercase tracking-[0.1em] mb-4" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
              About
            </p>
            <div className="flex items-center gap-3">
              <KivoIcon size={18} color="#111110" />
              <span className="text-[14px] text-[#8c8c88]" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                KIVO v1.0.0 · Engine: 127.0.0.1:8420
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Fade transition wrapper ───────────────────────────────────

function FadeScreen({ children, id }: { children: React.ReactNode; id: string }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(t);
  }, []);
  return (
    <div
      key={id}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(6px)",
        transition: "opacity 0.2s ease, transform 0.2s ease",
      }}
    >
      {children}
    </div>
  );
}

// ── App ───────────────────────────────────────────────────────

export default function App() {
  const [screen, setScreen] = useState<Screen>({ type: "loading" });
  const searchRef = useRef<HTMLInputElement>(null);

  const navigate = useCallback((next: Screen) => setScreen(next), []);

  useEffect(() => {
    if (screen.type !== "loading") return;
    const t = setTimeout(() => navigate({ type: "search" }), 1400);
    return () => clearTimeout(t);
  }, [screen.type, navigate]);

  const handleSelect = useCallback((id: string, query: string) => {
    if (query.trim()) {
      api.recordSelection(query, id).catch(() => {});
    }
    navigate({ type: "detail", entryId: id });
  }, [navigate]);

  useKeyboardShortcuts({
    screen,
    navigate,
    searchRef,
    onSave: screen.type === "edit" ? () => (window as any).__kivoSave?.() : undefined,
  });

  const screenKey = screen.type === "detail" ? `detail-${screen.entryId}` : screen.type;

  if (screen.type === "loading") return <LoadingScreen />;

  if (screen.type === "settings")
    return <FadeScreen id="settings"><SettingsScreen onBack={() => navigate({ type: "search" })} /></FadeScreen>;

  if (screen.type === "edit")
    return (
      <FadeScreen id={`edit-${screen.entryId ?? "new"}`}>
        <EditScreen entryId={screen.entryId} onSave={() => navigate({ type: "search" })} onBack={() => navigate({ type: "search" })} />
      </FadeScreen>
    );

  if (screen.type === "detail")
    return (
      <FadeScreen id={screenKey}>
        <DetailScreen
          entryId={screen.entryId}
          onSelect={handleSelect}
          onBack={() => navigate({ type: "search" })}
          onEdit={() => navigate({ type: "edit", entryId: screen.entryId })}
          onSettings={() => navigate({ type: "settings" })}
          searchRef={searchRef}
        />
      </FadeScreen>
    );

  return (
    <FadeScreen id="search">
      <SearchScreen
        onSelect={handleSelect}
        onEdit={() => navigate({ type: "edit", entryId: null })}
        onSettings={() => navigate({ type: "settings" })}
        searchRef={searchRef}
      />
    </FadeScreen>
  );
}
