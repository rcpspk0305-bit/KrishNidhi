"use client";

import { useEffect, useRef, useState } from "react";
import {
  ArrowUp,
  Leaf,
  Loader2,
  MessageCircle,
  RotateCcw,
  Square,
  Trash2,
  X,
} from "lucide-react";
import { useLanguage } from "./LanguageProvider";
import type { Locale } from "@/lib/i18n";
import styles from "./AssistantWidget.module.css";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  locale: Locale;
};
type Failure = "unavailable" | "connection" | "stopped" | "limited" | null;

export default function AssistantWidget() {
  const { t, locale } = useLanguage();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [failure, setFailure] = useState<Failure>(null);
  const [retryQuestion, setRetryQuestion] = useState("");
  const input = useRef<HTMLTextAreaElement>(null);
  const launcher = useRef<HTMLButtonElement>(null);
  const end = useRef<HTMLDivElement>(null);
  const controller = useRef<AbortController | null>(null);
  const requestVersion = useRef(0);
  const busy = useRef(false);

  useEffect(() => {
    if (open) input.current?.focus();
  }, [open]);
  useEffect(() => {
    end.current?.scrollIntoView({ block: "nearest" });
  }, [messages, sending]);
  useEffect(() => () => controller.current?.abort(), []);

  function close() {
    setOpen(false);
    launcher.current?.focus();
  }
  function stop() {
    requestVersion.current += 1;
    controller.current?.abort();
    busy.current = false;
    setSending(false);
    setFailure("stopped");
  }
  function clear() {
    requestVersion.current += 1;
    controller.current?.abort();
    busy.current = false;
    setSending(false);
    setMessages([]);
    setFailure(null);
    setRetryQuestion("");
    setDraft("");
    input.current?.focus();
  }

  async function sendQuestion(question: string, retry = false) {
    const text = question.trim();
    if (!text || text.length > 4000 || busy.current) return;
    busy.current = true;
    const version = ++requestVersion.current;
    const replyLocale = locale;
    const abortController = new AbortController();
    controller.current = abortController;
    const timeout = setTimeout(() => abortController.abort(), 60_000);
    const history = (retry ? messages.slice(0, -1) : messages)
      .slice(-10)
      .map(({ role, content }) => ({ role, content: content.slice(0, 4000) }));
    if (!retry)
      setMessages((previous) => [
        ...previous.slice(-99),
        {
          id: crypto.randomUUID(),
          role: "user",
          content: text,
          locale: replyLocale,
        },
      ]);
    setDraft("");
    setFailure(null);
    setRetryQuestion(text);
    setSending(true);
    try {
      const base = (
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
      ).replace(/\/$/, "");
      const response = await fetch(`${base}/assistant/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, language: replyLocale, history }),
        signal: abortController.signal,
      });
      if (version !== requestVersion.current) return;
      if (!response.ok) {
        setFailure(
          response.status === 429
            ? "limited"
            : response.status === 503
              ? "unavailable"
              : "connection",
        );
        return;
      }
      const data: unknown = await response.json();
      if (version !== requestVersion.current) return;
      if (
        typeof data !== "object" ||
        data === null ||
        !("reply" in data) ||
        typeof data.reply !== "string" ||
        !data.reply.trim()
      ) {
        setFailure("unavailable");
        return;
      }
      setMessages((previous) => [
        ...previous.slice(-99),
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.reply as string,
          locale: replyLocale,
        },
      ]);
      setRetryQuestion("");
    } catch {
      if (version === requestVersion.current) setFailure("connection");
    } finally {
      clearTimeout(timeout);
      if (version === requestVersion.current) {
        busy.current = false;
        setSending(false);
      }
    }
  }

  return (
    <div className={styles.widget}>
      {open && (
        <section
          id="krishinidhi-assistant"
          role="dialog"
          aria-modal="false"
          aria-labelledby="assistant-title"
          className={styles.panel}
          onKeyDown={(event) => {
            if (event.key === "Escape") close();
          }}
        >
          <header className={styles.header}>
            <span className={styles.mark}>
              <Leaf size={21} />
            </span>
            <div>
              <h2 id="assistant-title">{t("KrishiNidhi Assistant")}</h2>
              <p>{t("Ask anything, in your language.")}</p>
            </div>
            <button
              className={styles.iconButton}
              onClick={clear}
              aria-label={t("Clear conversation")}
              title={t("Clear conversation")}
            >
              <Trash2 size={17} />
            </button>
            <button
              className={styles.iconButton}
              onClick={close}
              aria-label={t("Close assistant")}
            >
              <X size={20} />
            </button>
          </header>
          <div
            className={styles.thread}
            role="log"
            aria-live="polite"
            aria-relevant="additions"
            aria-label={t("AI assistant")}
          >
            {messages.length === 0 && (
              <div className={styles.welcome}>
                <span>
                  <MessageCircle size={29} strokeWidth={1.5} />
                </span>
                <h3>{t("How can I help you today?")}</h3>
                <p>
                  {t("Ask about plant care, irrigation, or farmer schemes.")}
                </p>
                <div className={styles.suggestions}>
                  {[
                    "Explain this plant dashboard",
                    "Why is my device offline?",
                    "How often should I water a plant?",
                  ].map((question) => (
                    <button
                      key={question}
                      onClick={() => void sendQuestion(t(question))}
                    >
                      {t(question)}
                      <ArrowUp size={14} />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((message) => (
              <article
                key={message.id}
                className={
                  message.role === "user"
                    ? styles.userMessage
                    : styles.aiMessage
                }
              >
                <span className={styles.speaker}>
                  {t(message.role === "user" ? "You" : "AI assistant")}
                </span>
                <div lang={message.locale}>{message.content}</div>
              </article>
            ))}
            {sending && (
              <div className={styles.thinking} role="status">
                <Loader2 size={15} className={styles.spin} />
                {t("Thinking…")}
              </div>
            )}
            {failure && (
              <div className={styles.error} role="alert">
                <p>
                  {t(
                    failure === "limited"
                      ? "The assistant’s request limit has been reached. Please try again later."
                      : failure === "unavailable"
                        ? "AI replies are unavailable right now. Please try again later."
                        : failure === "stopped"
                          ? "Response stopped."
                          : "The connection was interrupted. Please try again.",
                  )}
                </p>
                {retryQuestion && (
                  <button
                    onClick={() => void sendQuestion(retryQuestion, true)}
                  >
                    <RotateCcw size={14} />
                    {t("Retry")}
                  </button>
                )}
              </div>
            )}
            <div ref={end} />
          </div>
          <form
            className={styles.composer}
            onSubmit={(event) => {
              event.preventDefault();
              void sendQuestion(draft);
            }}
          >
            <label htmlFor="assistant-question" className={styles.srOnly}>
              {t("Your question")}
            </label>
            <textarea
              ref={input}
              id="assistant-question"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder={t("Type your question…")}
              maxLength={4000}
              rows={2}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey &&
                  !event.nativeEvent.isComposing
                ) {
                  event.preventDefault();
                  void sendQuestion(draft);
                }
              }}
            />
            {sending ? (
              <button
                type="button"
                onClick={stop}
                className={styles.send}
                aria-label={t("Stop response")}
              >
                <Square size={15} />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!draft.trim()}
                className={styles.send}
                aria-label={t("Send question")}
              >
                <ArrowUp size={19} />
              </button>
            )}
          </form>
          <footer className={styles.disclaimer}>
            {t(
              "AI can make mistakes. It cannot control your pump or read live sensors.",
            )}
          </footer>
        </section>
      )}
      <button
        ref={launcher}
        className={styles.launcher}
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        aria-controls="krishinidhi-assistant"
        aria-label={t(open ? "Close assistant" : "Ask AI")}
      >
        {open ? <X size={21} /> : <MessageCircle size={21} />}
        <span>{t("Ask AI")}</span>
      </button>
    </div>
  );
}
