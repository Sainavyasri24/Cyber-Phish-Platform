function RiskMeter({ score }) {
  let color = "bg-green-500";
  if (score > 0.75) color = "bg-red-500";
  else if (score > 0.4) color = "bg-yellow-500";

  return (
    <div className="mt-4">
      <p>Threat Score: {score}</p>
      <div className="w-full bg-gray-600 rounded h-4">
        <div
          className={`${color} h-4 rounded`}
          style={{ width: `${score * 100}%` }}
        ></div>
      </div>
    </div>
  );
}

export default RiskMeter;