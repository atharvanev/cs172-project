"use client";

import { FormEvent, useState } from "react";
import Textbox from "@/components/textbox";
import Button from "@/components/button";
import Results from "@/components/results";
import type { SearchHit } from "@/types/search";

const SEARCH_API =
  process.env.NEXT_PUBLIC_SEARCH_API_URL ?? "http://127.0.0.1:5001";

export default function Home() {
  const [text, setText] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [results, setResults] = useState<SearchHit[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const query = text.trim();
    if (!query) {
      return;
    }

    setSubmittedQuery(query);
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ q: query, limit: "10" });
      const response = await fetch(`${SEARCH_API}/search?${params}`);
      if (!response.ok) {
        throw new Error(`Search failed (${response.status})`);
      }
      const data = (await response.json()) as { results: SearchHit[] };
      setResults(data.results ?? []);
    } catch {
      setResults([]);
      setError(
        "Could not reach the search API. Start it with: cd crawling && python search_api.py",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen items-center my-10 bg-white">
      <form
        className="flex items-center justify-center"
        onSubmit={handleSubmit}
      >
        <Textbox value={text} onChange={setText} />
        <Button disabled={text.trim().length === 0 || loading} />
      </form>
      <Results
        results={results}
        loading={loading}
        error={error}
        query={submittedQuery}
      />
    </div>
  );
}
