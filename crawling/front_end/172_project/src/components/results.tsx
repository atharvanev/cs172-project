import type { SearchHit } from "@/types/search";

type ResultsProps = {
  results: SearchHit[];
  loading: boolean;
  error: string | null;
  query: string;
};

const Results = ({ results, loading, error, query }: ResultsProps) => {
  if (loading) {
    return <p className="py-10 text-center text-gray-600">Searching…</p>;
  }

  if (error) {
    return <p className="py-10 text-center text-red-600">{error}</p>;
  }

  if (!query.trim()) {
    return null;
  }

  if (results.length === 0) {
    return (
      <p className="py-10 text-center text-gray-600">
        No results for &ldquo;{query}&rdquo;.
      </p>
    );
  }

  return (
    <ul className="mx-auto mt-8 max-w-3xl space-y-6 px-4">
      {results.map((hit) => (
        <li key={hit.url} className="border-b border-gray-200 pb-6">
          <a
            className="text-lg font-medium text-blue-700 hover:underline"
            href={hit.url}
            rel="noopener noreferrer"
            target="_blank"
          >
            {hit.title || hit.url}
          </a>
          <p className="text-sm text-green-800">{hit.url}</p>
          {hit.snippet ? (
            <p
              className="mt-2 text-sm text-gray-700"
              dangerouslySetInnerHTML={{ __html: hit.snippet }}
            />
          ) : null}
          <p className="mt-1 text-xs text-gray-500">
            score: {hit.score.toFixed(4)}
          </p>
        </li>
      ))}
    </ul>
  );
};

export default Results;
