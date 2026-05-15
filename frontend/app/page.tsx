"use client";

import { useState } from "react";

export default function Home() {

  const [file, setFile] = useState<File | null>(null);
  const [usn, setUsn] = useState("");
  const [result, setResult] = useState<any>(null);
  const [message, setMessage] = useState("");

  const BACKEND_URL = "https://vtu-result-backend.onrender.com";

  // Upload PDF

  const uploadPDF = async () => {

    if (!file) {
      setMessage("Please select a PDF file");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    try {

      const response = await fetch(
        `${BACKEND_URL}/upload-result`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      setMessage(data.message || "Result uploaded successfully");

    } catch (error) {

      setMessage(String(error));

    }
  };

  // Search Result

  const searchResult = async () => {

    if (!usn) {
      setMessage("Please enter USN");
      return;
    }

    try {

      const response = await fetch(
        `${BACKEND_URL}/get-result/${usn.toUpperCase()}`
      );

      const data = await response.json();

      setResult(data);

      if (data.detail) {
        setMessage("Student not found");
      } else {
        setMessage("Result fetched successfully");
      }

    } catch (error) {

      setMessage("Search failed");

    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-6 flex justify-center items-start">

      <div className="bg-white shadow-2xl rounded-2xl p-10 w-full max-w-4xl">

        <h1 className="text-4xl font-bold text-center text-blue-800 mb-3">
          VTU Result Management System
        </h1>

        <p className="text-center text-gray-700 mb-8 text-lg">
          Upload VTU PDFs and Search Student Results
        </p>

        {/* Message */}

        {message && (
          <div className="mb-6 bg-blue-100 border border-blue-400 text-blue-800 px-4 py-3 rounded-lg">
            {message}
          </div>
        )}

        {/* Upload Section */}

        <div className="mb-10">

          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Upload Result PDF
          </h2>

          <input
            type="file"
            accept=".pdf"
            onChange={(e) =>
              setFile(e.target.files?.[0] || null)
            }
            className="w-full border border-gray-400 p-3 rounded-lg text-gray-900"
          />

          <button
            onClick={uploadPDF}
            className="mt-4 bg-blue-700 hover:bg-blue-800 text-white px-6 py-3 rounded-lg w-full text-lg"
          >
            Upload PDF
          </button>

        </div>

        {/* Search Section */}

        <div className="mb-10">

          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Search Result by USN
          </h2>

          <input
            type="text"
            placeholder="Enter USN"
            value={usn}
            onChange={(e) => setUsn(e.target.value)}
            className="w-full border border-gray-400 p-3 rounded-lg text-gray-900"
          />

          <button
            onClick={searchResult}
            className="mt-4 bg-green-700 hover:bg-green-800 text-white px-6 py-3 rounded-lg w-full text-lg"
          >
            Search Result
          </button>

        </div>

        {/* Result Display */}

        {result && !result.detail && (

          <div className="bg-gray-50 border rounded-xl p-6">

            <h2 className="text-3xl font-bold text-blue-800 mb-6">
              Student Details
            </h2>

            <div className="grid grid-cols-2 gap-4 mb-8 text-gray-900">

              <div>
                <span className="font-bold">Name:</span> {result.name}
              </div>

              <div>
                <span className="font-bold">USN:</span> {result.usn}
              </div>

            </div>

            {/* Marks Table */}

            {result.subjects && (

              <table className="w-full border-collapse border border-gray-400">

                <thead>

                  <tr className="bg-blue-700 text-white">

                    <th className="border border-gray-400 p-3">
                      Subject
                    </th>

                    <th className="border border-gray-400 p-3">
                      Marks
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {result.subjects.map((subject: any, index: number) => (

                    <tr key={index} className="text-center text-gray-900">

                      <td className="border border-gray-400 p-3">
                        {subject.subject}
                      </td>

                      <td className="border border-gray-400 p-3">
                        {subject.marks}
                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            )}

          </div>

        )}

      </div>

    </main>
  );
}