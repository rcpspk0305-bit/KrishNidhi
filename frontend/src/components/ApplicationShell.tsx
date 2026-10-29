"use client";

import { Languages, Sprout } from "lucide-react";
import { isLocale, locales, localeNames } from "@/lib/i18n";
import { LanguageProvider, useLanguage } from "./LanguageProvider";
import AssistantWidget from "./AssistantWidget";
import styles from "./AssistantWidget.module.css";

function LanguageBar() {
  const { t, locale, setLocale } = useLanguage();
  return (
    <div className={styles.languageBar}>
      <span className={styles.wordmark}>
        <Sprout size={17} />
        KrishiNidhi
      </span>
      <label className={styles.languageControl}>
        <Languages size={17} />
        <span>{t("Language")}</span>
        <select
          aria-label={t("Application language")}
          value={locale}
          onChange={(event) => {
            if (isLocale(event.target.value)) setLocale(event.target.value);
          }}
        >
          {locales.map((language) => (
            <option key={language} value={language} lang={language}>
              {localeNames[language]}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

export default function ApplicationShell({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <LanguageProvider>
      <LanguageBar />
      {children}
      <AssistantWidget />
    </LanguageProvider>
  );
}
