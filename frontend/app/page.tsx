export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-6">

      <div className="bg-white shadow-xl rounded-2xl p-10 w-full max-w-2xl">

        <h1 className="text-4xl font-bold text-center text-blue-700 mb-4">
          VTU Result Management System
        </h1>

        <p className="text-center text-gray-600 mb-8">
          Upload VTU Result PDFs and Search Student Results
        </p>

        {/* Upload Section */}

        <div className="mb-8">

          <h2 className="text-xl font-semibold mb-3">
            Upload Result PDF
          </h2>

          <input
            type="file"
            className="w-full border p-3 rounded-lg"
          />

          <button
            className="mt-4 bg-blue-600 text-white px-6 py-3 rounded-lg w-full hover:bg-blue-700"
          >
            Upload PDF
          </button>

        </div>

        {/* Search Section */}

        <div>

          <h2 className="text-xl font-semibold mb-3">
            Search Result by USN
          </h2>

          <input
            type="text"
            placeholder="Enter USN"
            className="w-full border p-3 rounded-lg"
          />

          <button
            className="mt-4 bg-green-600 text-white px-6 py-3 rounded-lg w-full hover:bg-green-700"
          >
            Search Result
          </button>

        </div>

      </div>

    </main>
  );
}