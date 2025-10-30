"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type JsonValue = string | number | boolean | null | JsonObject | JsonArray;
type JsonObject = { [key: string]: JsonValue };
type JsonArray = JsonValue[];

type ApiResponse = JsonObject[];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8080/api";

function DocumentItem({ index, value }: { index: number; value: unknown }) {
  const [expanded, setExpanded] = useState(false);
  const pretty = useMemo(() => {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }, [value]);

  return (
    <div className={`card ${expanded ? "expanded" : ""}`}>
      <div className="card-header" onClick={() => setExpanded((v) => !v)} role="button">
        <div className="left">
          <span className="index">#{index + 1}</span>
          <span className="title">Документ</span>
        </div>
        <div className="right">
          <span className="chevron">{expanded ? "▾" : "▸"}</span>
        </div>
      </div>
      {expanded && (
        <pre className="card-body"><code>{pretty}</code></pre>
      )}
    </div>
  );
}

export default function Page() {
  const [documents, setDocuments] = useState<ApiResponse>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const intervalRef = useRef<number | null>(null);

  const endpoint = useMemo(() => `${API_BASE.replace(/\/$/, "")}/get_documents`, []);

  useEffect(() => {
    let isActive = true;
    const controller = new AbortController();

    async function fetchOnce() {
      try {
        const resp = await fetch(endpoint, { signal: controller.signal });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = (await resp.json()) as ApiResponse;
        if (!Array.isArray(data)) throw new Error("Некорректный формат ответа");
        if (isActive) {
          setDocuments(data);
          setError(null);
        }
      } catch (e: unknown) {
        if (isActive) setError(e instanceof Error ? e.message : "Неизвестная ошибка");
      } finally {
        if (isActive) setIsLoading(false);
      }
    }

    fetchOnce();
    intervalRef.current = window.setInterval(fetchOnce, 2000);

    return () => {
      isActive = false;
      controller.abort();
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [endpoint]);

  return (
    <div className="container">
      <header className="header">
        <h1>Документы</h1>
        <div className="status-row">
          <span className="endpoint">API: {endpoint}</span>
          {isLoading ? (
            <span className="badge loading">Загрузка…</span>
          ) : error ? (
            <span className="badge error">Ошибка: {error}</span>
          ) : (
            <span className="badge ok">Обновлено</span>
          )}
        </div>
      </header>

      <main>
        {documents.length === 0 && !isLoading && !error ? (
          <div className="empty">Пока нет документов</div>
        ) : null}
        <ul className="list">
          {documents.map((doc, idx) => (
            <li key={idx} className="list-item">
              <DocumentItem index={idx} value={doc} />
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
