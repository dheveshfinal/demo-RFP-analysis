"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  CheckCircle,
  ShieldAlert,
  Database,
  BarChart3,
  Settings,
  Upload,
  Search
} from "lucide-react";

export default function DashboardPage() {
  const [activeMenu, setActiveMenu] = useState("Dashboard");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [llmOutput, setLlmOutput] = useState(null);

  const router = useRouter();

  const menuItems = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "RFP Analyst", icon: FileText },
    { name: "Bid Decision", icon: CheckCircle },
    { name: "Compliance & Risk", icon: ShieldAlert },
    { name: "Tender DB", icon: Database },
    { name: "Reports", icon: BarChart3 },
    { name: "Settings", icon: Settings }
  ];

  const navigateToMyCompany = () => {
    router.push("/mycompany");
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const uploadRFP = async () => {
    if (!file) return alert("Please select a file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setLlmOutput(null);

      const res = await fetch("http://localhost:8000/api/rfp/upload", {
        method: "POST",
        body: formData
      });

      const data = await res.json();

      // Store only the analysis JSON or fallback to raw output
      setLlmOutput(data || data.result || data.output);

    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 text-gray-800">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold">AI Bids</h1>
          <p className="text-sm text-gray-500">Management Platform</p>
        </div>

        <nav className="p-4 space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.name}
              onClick={() => setActiveMenu(item.name)}
              className={`flex items-center w-full px-4 py-2 rounded-lg text-sm font-medium transition
                ${
                  activeMenu === item.name
                    ? "bg-blue-600 text-white"
                    : "hover:bg-gray-100"
                }`}
            >
              <item.icon className="w-4 h-4 mr-3" />
              {item.name}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b px-6 py-4 flex justify-between">
          <div className="relative w-1/2">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search opportunities, RFPs, or ask AI..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm"
            />
          </div>

          <div className="flex items-center gap-6">
            <button
              onClick={navigateToMyCompany}
              className="border rounded-lg px-3 py-2 text-sm"
            >
              Acme Corp
            </button>

            <div className="text-right">
              <p className="text-sm font-semibold">John Doe</p>
              <p className="text-xs text-gray-500">Bid Manager</p>
            </div>

            <div className="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center">
              JD
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Upload RFP */}
          <div className="bg-white rounded-xl border p-6">
            <h2 className="font-semibold mb-4">Upload New RFP</h2>

            <div className="border-2 border-dashed rounded-xl p-8 text-center">
              <Upload className="mx-auto h-8 w-8 text-gray-400 mb-3" />
              <input
                type="file"
                accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                onChange={handleFileChange}
                className="mb-4"
              />
              <button
                onClick={uploadRFP}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm"
              >
                {loading ? "Analyzing..." : "Quick Analyze"}
              </button>
            </div>
          </div>

          {/* LLM OUTPUT */}
          <div className="bg-white rounded-xl border p-6 min-h-[260px] overflow-auto">
            {loading && (
              <p className="text-gray-400 text-center">
                Analyzing RFP with AI...
              </p>
            )}
            {!loading && !llmOutput && (
              <p className="text-gray-400 text-center">
                AI analysis will appear here
              </p>
            )}
            {!loading && llmOutput && (
              <pre className="whitespace-pre-wrap text-sm text-gray-800">
                {typeof llmOutput === "string"
                  ? llmOutput
                  : JSON.stringify(llmOutput, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}