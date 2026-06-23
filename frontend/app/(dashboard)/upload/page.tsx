"use client";
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function UploadPage() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [currency, setCurrency] = useState("AED");
  const [region, setRegion] = useState("UAE");
  const [status, setStatus] = useState<"idle" | "uploading" | "processing" | "done" | "error">("idle");
  const [progress, setProgress] = useState("");

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    },
    maxSize: 15 * 1024 * 1024,
    multiple: false,
  });

  const handleSubmit = async () => {
    if (!file) return;
    setStatus("uploading");
    setProgress("Uploading file…");
    try {
      const token = await getToken();
      const { statement_id } = await api.upload(file, currency, region, token!);

      setStatus("processing");
      setProgress("AI is analyzing your statement…");

      // Poll for completion
      let done = false;
      for (let i = 0; i < 60 && !done; i++) {
        await new Promise((r) => setTimeout(r, 3000));
        const { status: s } = await api.status(statement_id, token!);
        if (s === "done") { done = true; setStatus("done"); }
        if (s === "failed") throw new Error("Processing failed");
      }

      router.push("/dashboard");
    } catch (e: any) {
      setStatus("error");
      setProgress(e.message || "Something went wrong.");
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Statement</h1>
        <p className="text-gray-500 text-sm mt-1">PDF, CSV, or Excel — up to 15 MB</p>
      </div>

      {/* Region + Currency */}
      <div className="flex gap-4">
        {[
          { label: "🇦🇪 UAE (AED)", r: "UAE", c: "AED" },
          { label: "🇮🇳 India (INR)", r: "India", c: "INR" },
        ].map((opt) => (
          <button key={opt.r}
            onClick={() => { setRegion(opt.r); setCurrency(opt.c); }}
            className={`flex-1 py-3 rounded-xl border text-sm font-medium transition
              ${region === opt.r ? "border-green-500 bg-green-50 text-green-700" : "border-gray-200 text-gray-600 hover:border-gray-300"}`}>
            {opt.label}
          </button>
        ))}
      </div>

      {/* Dropzone */}
      <div {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition
          ${isDragActive ? "border-green-400 bg-green-50" : "border-gray-200 hover:border-green-300"}`}>
        <input {...getInputProps()} />
        <div className="text-4xl mb-3">📁</div>
        {file ? (
          <p className="font-medium text-gray-900">{file.name}</p>
        ) : (
          <>
            <p className="font-medium text-gray-700">Drop your bank statement here</p>
            <p className="text-sm text-gray-400 mt-1">or click to browse</p>
          </>
        )}
      </div>

      {/* Submit */}
      <button onClick={handleSubmit}
        disabled={!file || status === "uploading" || status === "processing"}
        className="w-full py-4 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700
          disabled:opacity-50 disabled:cursor-not-allowed transition">
        {status === "uploading"  ? "Uploading…" :
         status === "processing" ? "AI Analyzing… (1–2 min)" :
         "Analyze My Finances →"}
      </button>

      {/* Status */}
      {progress && (
        <div className={`p-4 rounded-xl text-sm text-center
          ${status === "error" ? "bg-red-50 text-red-600" : "bg-blue-50 text-blue-700"}`}>
          {progress}
        </div>
      )}

      {/* Tips */}
      <div className="bg-gray-50 rounded-xl p-5 text-sm text-gray-500 space-y-1">
        <p className="font-medium text-gray-700 mb-2">Tips for best results:</p>
        <p>• Use text-based PDFs (not scanned photos)</p>
        <p>• CSV exports from your bank app work great</p>
        <p>• Include at least 1 month of transactions</p>
      </div>
    </div>
  );
}
