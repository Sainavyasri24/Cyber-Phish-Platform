import { useState, useEffect } from "react";

function Settings() {
    const [sensitivity, setSensitivity] = useState("Standard");
    const [apiKey, setApiKey] = useState("");
    const [showKey, setShowKey] = useState(false);

    useEffect(() => {
        const savedSensitivity = localStorage.getItem("phish_sensitivity") || "Standard";
        const savedKey = localStorage.getItem("phish_vt_key") || "";
        setSensitivity(savedSensitivity);
        setApiKey(savedKey);
    }, []);

    const handleSave = () => {
        localStorage.setItem("phish_sensitivity", sensitivity);
        localStorage.setItem("phish_vt_key", apiKey);
        alert("Settings saved successfully!");
    };

    return (
        <div className="max-w-4xl text-white animate-fade-in">
            <h2 className="text-2xl font-bold mb-6 font-serif">Settings</h2>

            <div className="space-y-8">

                {/* Scanning Sensitivity */}
                <div className="bg-[#1a1a1a] p-6 rounded-sm border border-gray-800">
                    <h3 className="text-lg font-semibold mb-4 text-blue-400">Scanning Sensitivity</h3>
                    <p className="text-sm text-gray-400 mb-4">
                        Adjust how aggressive the phishing detection engine should be.
                        High sensitivity may produce more false positives.
                    </p>

                    <div className="flex gap-4">
                        {["Standard", "High"].map((level) => (
                            <button
                                key={level}
                                onClick={() => setSensitivity(level)}
                                className={`px-4 py-2 rounded-sm border transition-colors ${sensitivity === level
                                        ? "bg-blue-600 border-blue-600 text-white"
                                        : "bg-transparent border-gray-600 text-gray-300 hover:border-gray-400"
                                    }`}
                            >
                                {level}
                            </button>
                        ))}
                    </div>
                </div>

                {/* API Integration */}
                <div className="bg-[#1a1a1a] p-6 rounded-sm border border-gray-800">
                    <h3 className="text-lg font-semibold mb-4 text-purple-400">External Integrations</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">
                                VirusTotal API Key (Optional)
                            </label>
                            <div className="flex relative">
                                <input
                                    type={showKey ? "text" : "password"}
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    placeholder="Enter your API key"
                                    className="flex-1 bg-black border border-gray-700 rounded-sm py-2 px-3 text-white focus:outline-none focus:border-purple-500"
                                />
                                <button
                                    onClick={() => setShowKey(!showKey)}
                                    className="absolute right-3 top-2 text-gray-500 hover:text-gray-300 text-xs"
                                >
                                    {showKey ? "HIDE" : "SHOW"}
                                </button>
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                                Used to fetch real-time reputation data for high-risk URLs.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Save Button */}
                <div>
                    <button
                        onClick={handleSave}
                        className="bg-green-600 hover:bg-green-700 text-white px-8 py-2 rounded-sm font-semibold transition-colors shadow-sm"
                    >
                        Save Configuration
                    </button>
                </div>

            </div>
        </div>
    );
}

export default Settings;
