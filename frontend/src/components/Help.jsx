import { useState } from "react";

function Help() {
    const [openIndex, setOpenIndex] = useState(null);

    const faqs = [
        {
            question: "What do the risk levels mean?",
            answer: "High Risk means the URL is on a blacklist or exhibits strong malicious indicators. Medium Risk suggests suspicious patterns (like IP usage or weird domains). Low Risk means no immediate threats were found."
        },
        {
            question: "How accurate is the scanner?",
            answer: "The scanner uses a combination of threat intelligence feeds (blacklists) and heuristic analysis. While very effective, no security tool is 100% perfect. Always exercise caution."
        },
        {
            question: "Can I use the API for my own app?",
            answer: "Yes, you can use the backend API endpoints (/scan-url) to integrate scanning into your own workflows. See the developer documentation for details."
        }
    ];

    return (
        <div className="max-w-4xl text-white animate-fade-in">
            <h2 className="text-2xl font-bold mb-6 font-serif">Help Center</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                {/* FAQ Section */}
                <div>
                    <h3 className="text-xl font-semibold mb-4 text-gray-300">Frequently Asked Questions</h3>
                    <div className="space-y-4">
                        {faqs.map((faq, idx) => (
                            <div key={idx} className="bg-[#1a1a1a] rounded-sm border border-gray-800 overflow-hidden">
                                <button
                                    onClick={() => setOpenIndex(active => active === idx ? null : idx)}
                                    className="w-full text-left px-4 py-3 font-medium flex justify-between items-center hover:bg-gray-800 transition-colors"
                                >
                                    {faq.question}
                                    <span className="text-gray-500">{openIndex === idx ? "−" : "+"}</span>
                                </button>
                                {openIndex === idx && (
                                    <div className="px-4 py-3 bg-black text-gray-400 text-sm border-t border-gray-800">
                                        {faq.answer}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Contact Support */}
                <div className="bg-[#1a1a1a] p-6 rounded-sm border border-gray-800 h-fit">
                    <h3 className="text-xl font-semibold mb-4 text-purple-400">Contact Support</h3>
                    <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Subject</label>
                            <select className="w-full bg-black border border-gray-700 rounded-sm p-2 text-white focus:border-purple-500 outline-none">
                                <option>Report a Bug</option>
                                <option>False Positive Report</option>
                                <option>Feature Request</option>
                                <option>Other</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Message</label>
                            <textarea
                                rows="4"
                                className="w-full bg-black border border-gray-700 rounded-sm p-2 text-white focus:border-purple-500 outline-none resize-none"
                                placeholder="Describe your issue..."
                            ></textarea>
                        </div>
                        <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 rounded-sm transition-colors">
                            Send Message
                        </button>
                    </form>
                </div>

            </div>
        </div>
    );
}

export default Help;
