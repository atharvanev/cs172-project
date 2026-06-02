"use client";

type TextboxProps = {
  value: string;
  onChange: (value: string) => void;
};

const Textbox = ({ value, onChange }: TextboxProps) => {
  return (
    <input
      className="h-10 w-96 rounded-l-md border border-gray-900 px-3 text-sm text-gray-900 placeholder:text-gray-400"
      onChange={(event) => onChange(event.target.value)}
      placeholder="Type here..."
      type="text"
      value={value}
    />
  );
};

export default Textbox;
