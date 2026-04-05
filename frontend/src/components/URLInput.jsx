import { useState } from "react";

function URLInput({ onScan }) {
  const [url, setUrl] = useState("");

  return (
    <div className="flex gap-4">
      <input
        type="text"
        placeholder="ENTER TARGET URL (e.g., http://suspicious-link.com)"
        className="cyber-input flex-1 font-mono text-sm"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button
        onClick={() => onScan(url)}
        className="cyber-btn-primary min-w-[120px]"
      >
        INITIATE SCAN
      </button>
    </div>
  );
}

export default URLInput;