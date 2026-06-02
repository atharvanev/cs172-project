"use client";
import { useState } from "react";
import Textbox from "@/components/textbox";
import Button from "@/components/button";
import Results from "@/components/results";

export default function Home() {
  const [text, setText] = useState("");
  const handleSubmit = () => {/*Use FastAPI or Flask to submit to searcher*/};

  return (
    <div className="min-h-screen items-center my-10 bg-white">
      <form
        className="flex items-center justify-center"
        onSubmit={handleSubmit}
      >
        <Textbox value={text} onChange={setText} />
        <Button disabled={text.trim().length === 0} />
      </form>
      <Results/>
    </div>
  );
}
