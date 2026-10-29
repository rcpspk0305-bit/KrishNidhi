"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useSyncExternalStore,
} from "react";
import { isLocale, localeTags, translate, type Locale } from "@/lib/i18n";

const STORAGE_KEY = "krishinidhi-language";
const CHANGE_EVENT = "krishinidhi-language-change";
let memoryLocale: Locale = "en";

function snapshot(): Locale {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return isLocale(stored) ? stored : memoryLocale;
  } catch {
    return memoryLocale;
  }
}

function subscribe(callback: () => void) {
  const storageListener = (event: StorageEvent) => {
    if (event.key === STORAGE_KEY || event.key === null) callback();
  };
  window.addEventListener("storage", storageListener);
  window.addEventListener(CHANGE_EVENT, callback);
  return () => {
    window.removeEventListener("storage", storageListener);
    window.removeEventListener(CHANGE_EVENT, callback);
  };
}

type LanguageContextValue = {
  locale: Locale;
  intlLocale: string;
  setLocale: (locale: Locale) => void;
  t: (value: string | number | null | undefined) => string;
};
const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const locale = useSyncExternalStore(
    subscribe,
    snapshot,
    () => "en" as Locale,
  );
  const setLocale = useCallback((next: Locale) => {
    memoryLocale = next;
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* Preference still works for this session. */
    }
    window.dispatchEvent(new Event(CHANGE_EVENT));
  }, []);
  const t = useCallback(
    (value: string | number | null | undefined) => translate(value, locale),
    [locale],
  );
  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);
  return (
    <LanguageContext.Provider
      value={{ locale, intlLocale: localeTags[locale], setLocale, t }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context)
    throw new Error("useLanguage must be used within LanguageProvider");
  return context;
}
