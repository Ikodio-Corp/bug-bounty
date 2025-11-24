"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

interface Bug {
  id: number;
  title: string;
  severity: string;
  status: string;
  bounty_amount: number;
  target_url: string;
  created_at: string;
  validated: boolean;
}

export default function BugsPage() {
  const router = useRouter();
  const [bugs, setBugs] = useState<Bug[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [showNewBugModal, setShowNewBugModal] = useState(false);

  useEffect(() => {
    fetchBugs();
  }, [filter]);

  const fetchBugs = async () => {
    try {
      const response = await api.get("/bugs", {
        params: filter !== "all" ? { status: filter } : {},
      });
      setBugs(response.data);
    } catch (error) {
      console.error("Failed to fetch bugs:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Bug Reports</h1>
        <Link
          href="/bugs/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Report Bug
        </Link>
      </div>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-2 rounded-lg transition ${
            filter === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter("pending")}
          className={`px-4 py-2 rounded-lg transition ${
            filter === "pending"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          Pending
        </button>
        <button
          onClick={() => setFilter("validated")}
          className={`px-4 py-2 rounded-lg transition ${
            filter === "validated"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          Validated
        </button>
        <button
          onClick={() => setFilter("fixed")}
          className={`px-4 py-2 rounded-lg transition ${
            filter === "fixed"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          Fixed
        </button>
      </div>

      {bugs.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No bugs found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {bugs.map((bug) => (
            <Link
              key={bug.id}
              href={`/bugs/${bug.id}`}
              className="block bg-white rounded-lg shadow hover:shadow-lg transition p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{bug.title}</h3>
                  <p className="text-gray-600 mb-4 line-clamp-2">
                    {bug.description}
                  </p>
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-3 py-1 rounded text-sm ${
                        bug.status === "validated"
                          ? "bg-green-100 text-green-800"
                          : bug.status === "pending"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {bug.status}
                    </span>
                    <span
                      className={`px-3 py-1 rounded text-sm ${
                        bug.severity === "critical"
                          ? "bg-red-100 text-red-800"
                          : bug.severity === "high"
                          ? "bg-orange-100 text-orange-800"
                          : "bg-blue-100 text-blue-800"
                      }`}
                    >
                      {bug.severity}
                    </span>
                    <span className="text-sm text-gray-500">
                      by {bug.reporter_name}
                    </span>
                  </div>
                </div>
                <div className="ml-4 text-right">
                  <p className="text-2xl font-bold text-green-600">
                    ${bug.bounty_amount}
                  </p>
                  <p className="text-sm text-gray-500">Bounty</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
