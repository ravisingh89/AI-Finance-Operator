export function LoadingSpinner({ text = "Loading…" }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-3 text-gray-400">
      <div className="w-8 h-8 border-4 border-gray-200 border-t-green-500 rounded-full animate-spin" />
      <p className="text-sm">{text}</p>
    </div>
  );
}
