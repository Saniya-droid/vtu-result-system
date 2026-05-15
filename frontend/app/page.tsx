"use client";

import { useState } from "react";

export default function Home() {

  const [file, setFile] = useState<File | null>(null);
  const [usn, setUsn] = useState("");
  const [result, setResult] = useState<any>(null);

  const BACKEND_URL = "https://vtu-result-backend.onrender.com";

  // Upload PDF

  const uploadPDF = async () => {
  alert("Upload button clicked");

    if (!file) {
      alert("Please select PDF");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
      `${BACKEND_URL}/upload-result`,
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    alert(data.message);
  };

  // Search Result

  const searchResult = async () => {

    if (!usn) {
      alert("Enter USN");
      return;
    }

    const response = await fetch(
      `${BACKEND_URL}/get-result/${usn}`
    );

    const data = await response.json();

    setResult(data);
  };

  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-6">

      <div className="bg-white shadow-xl rounded-2xl p-10 w-full max-w-3xl">

        <h1 className="text-4xl font-bold text-center text-blue-700 mb-4">
          VTU RESULT SYSTEM TEST
        </h1>

        <p className="text-center text-gray-600 mb-8">
          Upload VTU Result PDFs and Search Results
        </p>

        {/* Upload */}

        <div className="mb-10">

          <h2 className="text-xl font-semibold mb-3">
            Upload Result PDF
          </h2>

          <input
            type="file"
            accept=".pdf"
            onChange={(e) =>
              setFile(e.target.files?.[0] || null)
            }
            className="w-full border p-3 rounded-lg"
          />

          <button
            onClick={uploadPDF}
            className="mt-4 bg-blue-600 text-white px-6 py-3 rounded-lg w-full"
          >
            Upload PDF
          </button>

        </div>

        {/* Search */}

        <div>

          <h2 className="text-xl font-semibold mb-3">
            Search Result by USN
          </h2>

          <input
            type="text"
            placeholder="Enter USN"
            value={usn}
            onChange={(e) => setUsn(e.target.value)}
            className="w-full border p-3 rounded-lg"
          />

          <button
            onClick={searchResult}
            className="mt-4 bg-green-600 text-white px-6 py-3 rounded-lg w-full"
          >
            Search Result
          </button>

        </div>

        {/* Result */}

        {result && (

          <div className="mt-10">

            <h2 className="text-2xl font-bold mb-4">
              Student Result
            </h2>

            <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>

          </div>
        )}

      </div>

    </main>
  );
}