type ButtonProps = {
  disabled?: boolean;
};

const Button = ({ disabled = false }: ButtonProps) => {
  return (
    <button
      className="h-10 rounded-r-md border border-l-0 border-gray-900 bg-gray-900 px-4 text-sm font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
      disabled={disabled}
      type="submit"
    >
      Search
    </button>
  );
};

export default Button;
