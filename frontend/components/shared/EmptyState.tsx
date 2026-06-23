import Link from "next/link";

interface Props {
  message?: string;
  showUploadLink?: boolean;
}

export function EmptyState({
  message = "No data yet. Upload a bank statement to get started.",
  showUploadLink = true,
}: Props) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-4 text-center">
      <p className="text-4xl">📁</p>
      <p className="text-gray-500 max-w-xs">{message}</p>
      {showUploadLink && (
        <Link
          href="/upload"
          className="px-5 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition"
        >
          Upload Statement →
        </Link>
      )}
    </div>
  );
}
