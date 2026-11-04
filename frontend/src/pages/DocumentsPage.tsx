import { useCallback, useRef, useState } from "react";
import {
  FileText,
  Upload,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Inbox,
} from "lucide-react";
import type { Document } from "../lib/api";
import { uploadDocument, fetchDocuments } from "../lib/api";

type UploadStatus = "idle" | "uploading" | "success" | "error";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Load documents ──
  const loadDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch {
      // API not implemented yet — keep empty list
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load once on mount
  useState(() => {
    loadDocuments();
  });

  // ── File selection ──
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setSelectedFile(file);
    setUploadStatus("idle");
    setErrorMessage("");
  };

  // ── Upload ──
  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus("uploading");
    setErrorMessage("");

    try {
      await uploadDocument(selectedFile);
      setUploadStatus("success");
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      await loadDocuments();
    } catch (err) {
      setUploadStatus("error");
      setErrorMessage(
        err instanceof Error ? err.message : "Upload failed",
      );
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      {/* ── Header ── */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Documents</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload PDF or TXT files to build your knowledge base.
        </p>
      </div>

      {/* ── Upload area ── */}
      <div className="mb-10 rounded-lg border border-dashed border-gray-300 bg-white p-6">
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-indigo-50 text-indigo-600">
              <Upload className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">
                {selectedFile ? selectedFile.name : "Choose a file"}
              </p>
              <p className="text-xs text-gray-400">PDF or TXT, up to 20 MB</p>
            </div>
          </div>

          <div className="flex gap-3">
            <label className="cursor-pointer rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50">
              Browse
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt"
                className="hidden"
                onChange={handleFileSelect}
              />
            </label>

            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploadStatus === "uploading"}
              className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploadStatus === "uploading" && (
                <Loader2 className="h-4 w-4 animate-spin" />
              )}
              Upload
            </button>
          </div>
        </div>

        {/* Status messages */}
        {uploadStatus === "success" && (
          <div className="mt-4 flex items-center gap-2 text-sm text-green-600">
            <CheckCircle2 className="h-4 w-4" />
            File uploaded successfully.
          </div>
        )}
        {uploadStatus === "error" && (
          <div className="mt-4 flex items-center gap-2 text-sm text-red-600">
            <AlertCircle className="h-4 w-4" />
            {errorMessage}
          </div>
        )}
      </div>

      {/* ── Document list ── */}
      {loading ? (
        <div className="flex items-center justify-center py-20 text-gray-400">
          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          Loading documents…
        </div>
      ) : documents.length === 0 ? (
        /* Empty state */
        <div className="flex flex-col items-center justify-center rounded-lg border border-gray-200 bg-white py-20 text-center">
          <Inbox className="mb-3 h-10 w-10 text-gray-300" />
          <p className="text-sm font-medium text-gray-500">
            No documents yet
          </p>
          <p className="mt-1 text-xs text-gray-400">
            Upload a PDF or TXT file to get started.
          </p>
        </div>
      ) : (
        /* Table */
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-gray-200 bg-gray-50 text-xs font-medium uppercase tracking-wider text-gray-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Uploaded</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="flex items-center gap-2 px-4 py-3 font-medium text-gray-800">
                    <FileText className="h-4 w-4 text-gray-400" />
                    {doc.filename}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{doc.file_type}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        doc.status === "ready"
                          ? "bg-green-50 text-green-700"
                          : doc.status === "processing"
                            ? "bg-yellow-50 text-yellow-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

