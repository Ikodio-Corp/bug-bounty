"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

interface Guild {
  id: number;
  name: string;
  description: string;
  member_count: number;
  total_bounties: number;
  reputation_score: number;
  created_at: string;
  is_member: boolean;
}

export default function GuildsPage() {
  const router = useRouter();
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchGuilds();
  }, []);

  const fetchGuilds = async () => {
    try {
      const response = await api.get("/guilds");
      setGuilds(response.data);
    } catch (error) {
      console.error("Failed to fetch guilds:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Security Guilds</h1>
        <Link
          href="/guilds/create"
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          Create Guild
        </Link>
      </div>

      <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-2">What are Security Guilds?</h2>
        <p className="text-gray-700">
          Join forces with other security researchers. Share knowledge, collaborate on
          bounties, and gain access to exclusive opportunities. Progress through tiers
          to unlock more benefits.
        </p>
      </div>

      {guilds.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No guilds available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {guilds.map((guild) => (
            <div
              key={guild.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-2xl font-bold">{guild.name}</h3>
                    <span className="inline-block mt-2 px-3 py-1 bg-indigo-100 text-indigo-800 text-sm rounded-full">
                      {guild.tier_name}
                    </span>
                  </div>
                  {guild.is_member && (
                    <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                      Member
                    </span>
                  )}
                </div>

                <p className="text-gray-600 mb-6">{guild.description}</p>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-indigo-600">
                      {guild.member_count}
                    </p>
                    <p className="text-sm text-gray-500">Members</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      ${guild.total_bounty_pool}
                    </p>
                    <p className="text-sm text-gray-500">Bounty Pool</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {guild.required_reputation}
                    </p>
                    <p className="text-sm text-gray-500">Min Reputation</p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Link
                    href={`/guilds/${guild.id}`}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-center"
                  >
                    View Details
                  </Link>
                  {!guild.is_member && (
                    <button
                      onClick={() => handleJoinGuild(guild.id)}
                      className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                    >
                      Join Guild
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
