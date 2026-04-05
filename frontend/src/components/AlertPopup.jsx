function AlertPopup({ risk }) {
  let msg = "Safe URL";
  let color = "bg-green-600";

  if (risk === "High") {
    msg = "URL BLOCKED – Phishing Detected!";
    color = "bg-red-600";
  } else if (risk === "Medium") {
    msg = "Warning: Suspicious URL";
    color = "bg-yellow-600";
  }

  return (
    <div className={`${color} p-3 mt-4 rounded`}>
      {msg}
    </div>
  );
}

export default AlertPopup;