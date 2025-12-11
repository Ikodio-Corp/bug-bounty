"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface BugDetail {
  id: number;
  title: string;
  target_url: string;
  severity: string;
  status: string;
  vulnerability_type: string;
  description: string;
  reproduction_steps: string;
  impact: string;
  recommendation: string;
  bounty_amount: number;
  validated: boolean;
  created_at: string;
  updated_at: string;
  hunter: {
    id: number;
    username: string;
    reputation_score: number;
  };
}

export default function BugDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [bug, setBug] = useState<BugDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBugDetail();
  }, [params.id]);

  const fetchBugDetail = async () => {
    try {
      const response = await api.get(`/bugs/${params.id}`);
      setBug(response.data);
    } catch (error) {
      console.error("Failed to fetch bug details:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "text-red-400 bg-red-500/10 border-red-500/50";
      case "high":
        return "text-orange-400 bg-orange-500/10 border-orange-500/50";
      case "medium":
        return "text-yellow-400 bg-yellow-500/10 border-yellow-500/50";
      case "low":
        return "text-gray-400 bg-white/10 border-white/50";
      default:
        return "text-slate-400 bg-slate-500/10 border-slate-500/50";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "validated":
        return "text-green-400 bg-green-500/10";
      case "pending":
        return "text-yellow-400 bg-yellow-500/10";
      case "rejected":
        return "text-red-400 bg-red-500/10";
      case "paid":
        return "text-gray-400 bg-white/10";
      default:
        return "text-slate-400 bg-slate-500/10";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
          <p className="text-slate-400 mt-4">Loading bug details...</p>
        </div>
      </div>
    );
  }

  if (!bug) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-400 text-lg">Bug report not found</p>
          <button
            onClick={() => router.push("/bugs")}
            className="mt-4 px-6 py-3 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition"
          >
            Back to Bug Reports
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="lg:ml-64">
        <div className="p-8">
          <button
            onClick={() => router.push("/bugs")}
            className="flex items-center text-slate-400 hover:text-white mb-6 transition"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Bug Reports
          </button>

          <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-lg p-6 mb-8">
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-3">
                  <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getSeverityColor(bug.severity)}`}>
                    {bug.severity.toUpperCase()}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(bug.status)}`}>
                    {bug.status.toUpperCase()}
                  </span>
                  {bug.validated && (
                    <span className="flex items-center text-green-400 text-sm">
                      <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Validated
                    </span>
                  )}
                </div>
                <h1 className="text-2xl font-bold text-white mb-2">{bug.title}</h1>
                <p className="text-slate-400">{bug.target_url}</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-yellow-400 mb-1">${bug.bounty_amount.toLocaleString()}</p>
                <p className="text-sm text-slate-400">bounty amount</p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-slate-800">
              <div>
                <p className="text-sm text-slate-400 mb-1">Reported By</p>
                <p className="text-white font-semibold">{bug.hunter.username}</p>
                <p className="text-xs text-slate-500">{bug.hunter.reputation_score} reputation</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Vulnerability Type</p>
                <p className="text-white font-semibold">{bug.vulnerability_type.replace(/_/g, ' ').toUpperCase()}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Reported</p>
                <p className="text-white font-semibold">{new Date(bug.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Last Updated</p>
                <p className="text-white font-semibold">{new Date(bug.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6">
            <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Description</h2>
              <p className="text-slate-300 whitespace-pre-wrap">{bug.description}</p>
            </div>

            <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Reproduction Steps</h2>
              <div className="text-slate-300 whitespace-pre-wrap">{bug.reproduction_steps}</div>
            </div>

            <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Impact</h2>
              <p className="text-slate-300 whitespace-pre-wrap">{bug.impact}</p>
            </div>

            {bug.recommendation && (
              <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-lg p-6">
                <h2 className="text-xl font-bold text-white mb-4">Recommendation</h2>
                <p className="text-slate-300 whitespace-pre-wrap">{bug.recommendation}</p>
              </div>
            )}
          </div>

          <div className="mt-8 flex space-x-4">
            <button className="px-6 py-3 bg-cyan-600 text-white rounded-lg font-semibold hover:bg-cyan-500 transition">
              Export Report
            </button>
            <button className="px-6 py-3 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition">
              Share
            </button>
            {bug.status === "validated" && (
              <button className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-500 transition">
                Request Payment
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
