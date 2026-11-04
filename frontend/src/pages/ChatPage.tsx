import { useRef, useState } from "react";
import {
  Send,
  Loader2,
  MessageSquare,
  FileText,
  AlertCircle,
} from "lucide-react";
import type { ChatMessage } from "../lib/api";
import { sendChatMessage } from "../lib/api";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);
    setError("");

    try {
      const reply = await sendChatMessage(text);
      setMessages((prev) => [...prev, reply]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to get a response",
      );
    } finally {
      setSending(false);
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col px-4 py-6">
      {/* ── Messages area ── */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          /* Empty state */
          <div className="flex h-full flex-col items-center justify-center text-center">
            <MessageSquare className="mb-3 h-10 w-10 text-gray-300" />
            <p className="text-sm font-medium text-gray-500">
              Ask a question about your documents
            </p>
            <p className="mt-1 max-w-xs text-xs text-gray-400">
              DocuMind AI will search your uploaded files and answer using
              relevant context.
            </p>
          </div>
        ) : (
          <div className="space-y-6 pb-4">
            {messages.map((msg, i) => (
              <div key={i}>
                {/* Message bubble */}
                <div
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-indigo-600 text-white"
                        : "border border-gray-200 bg-white text-gray-800"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>

                {/* Source citations */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2 pl-1">
                    {msg.sources.map((src, j) => (
                      <span
                        key={j}
                        className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-1 text-xs text-gray-500"
                      >
                        <FileText className="h-3 w-3" />
                        {src.document}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Thinking indicator */}
            {sending && (
              <div className="flex justify-start">
                <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-gray-400">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Thinking…
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div className="mb-3 flex items-center gap-2 rounded-md bg-red-50 px-4 py-2 text-sm text-red-600">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* ── Input bar ── */}
      <div className="shrink-0 rounded-lg border border-gray-200 bg-white p-2 shadow-sm">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your documents…"
            rows={1}
            className="flex-1 resize-none rounded-md bg-transparent px-3 py-2 text-sm outline-none placeholder:text-gray-400"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-indigo-600 text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

