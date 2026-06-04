export type SearchHit = {
  url: string;
  title: string;
  score: number;
  snippet: string;
  outgoing_links: string[];
};

export type SearchResponse = {
  results: SearchHit[];
};
