function RiskCard({ data }) {
  const { details } = data;

  // Risk-level styling
  const riskStyles = {
    High:   { color: "text-red-500",    bg: "bg-red-500",    border: "border-red-800",    icon: "❌", label: "Malicious URL" },
    Medium: { color: "text-yellow-400", bg: "bg-yellow-400", border: "border-yellow-800", icon: "⚠️", label: "Suspicious URL" },
    Low:    { color: "text-green-400",  bg: "bg-green-400",  border: "border-green-800",  icon: "✅", label: "Safe URL" },
  };
  const style = riskStyles[data.risk_level] ?? riskStyles.Low;

  // Format threat score as percentage
  const scorePercent = Math.round((data.threat_score ?? 0) * 100);

  return (
    <div className="text-white font-sans text-sm animate-fade-in space-y-6">

      {/* ── Top summary banner ── */}
      <div className={`flex items-center gap-4 p-4 rounded border ${style.border} bg-gray-900/60`}>
        <span className="text-3xl">{style.icon}</span>
        <div className="flex-1">
          <p className={`text-lg font-bold ${style.color}`}>{style.label}</p>
          <p className="text-gray-400 text-xs mt-0.5 truncate">{data.url}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Threat Score</p>
          <p className={`text-3xl font-bold ${style.color}`}>{scorePercent}%</p>
        </div>
      </div>

      {/* ── Threat Meter ── */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Threat Level</span>
          <span className={style.color}>{data.risk_level} Risk</span>
        </div>
        <div className="w-full h-2.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${style.bg}`}
            style={{ width: `${scorePercent}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-700 mt-1">
          <span>0%</span>
          <span>100%</span>
        </div>
      </div>

      {/* ── Meta info ── */}
      <div className="grid grid-cols-3 gap-4 text-center">
        <MetaBox label="Action" value={data.action} />
        <MetaBox label="Model" value={data.model ?? "—"} />
        <MetaBox label="Scanned At" value={data.timestamp} small />
      </div>

      {/* ── Feature details ── */}
      {details && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* URL Analysis */}
          <div className="bg-[#111] rounded border border-gray-800 p-4 space-y-2">
            <h3 className="font-bold text-blue-400 mb-3 text-xs uppercase tracking-wider">
              URL Analysis
            </h3>
            <FeatureRow label="Length"       value={`${details.url_features.url_length} chars`} />
            <FeatureRow label="Dot Count"    value={details.url_features.dot_count} />
            <FeatureRow label="Special Chars" value={details.url_features.special_chars} />
            <FeatureRow label="HTTPS"
              value={details.url_features.https_present ? "Yes ✅" : "No ⚠️"}
              highlight={!details.url_features.https_present}
            />
            <FeatureRow label="IP Address"
              value={details.url_features.is_ip_address ? "Yes ⚠️" : "No ✅"}
              highlight={details.url_features.is_ip_address}
            />
          </div>

          {/* Network Diagnostics */}
          <div className="bg-[#111] rounded border border-gray-800 p-4 space-y-2">
            <h3 className="font-bold text-purple-400 mb-3 text-xs uppercase tracking-wider">
              Network Diagnostics
            </h3>
            <FeatureRow label="ASN Risk"
              value={details.network_features.asn_risk ? "High ⚠️" : "Low ✅"}
              highlight={details.network_features.asn_risk}
            />
            <FeatureRow label="DNS TTL"   value={`${details.network_features.dns_ttl}s`} />
            <FeatureRow label="Domain Age" value={`${details.network_features.domain_age_days} days`}
              highlight={details.network_features.domain_age_days < 30}
            />
            <FeatureRow label="Packet Rate" value={`${Math.round(details.network_features.packet_rate)} /sec`} />
            <FeatureRow label="Flow Duration" value={`${Math.round(details.network_features.flow_duration)}s`} />
          </div>
        </div>
      )}
    </div>
  );
}

function MetaBox({ label, value, small = false }) {
  return (
    <div className="bg-[#111] rounded border border-gray-800 px-3 py-2">
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <p className={`font-semibold text-white ${small ? "text-xs" : "text-sm"} break-all`}>{value}</p>
    </div>
  );
}

function FeatureRow({ label, value, highlight = false }) {
  return (
    <div className="flex justify-between items-center text-xs">
      <span className="text-gray-500">{label}</span>
      <span className={highlight ? "text-yellow-400 font-semibold" : "text-gray-200"}>{value}</span>
    </div>
  );
}

export default RiskCard;