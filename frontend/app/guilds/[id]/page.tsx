"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface GuildMember {
  id: number;
  username: string;
  reputation_score: number;
  bugs_found: number;
  bounties_earned: number;
  joined_at: string;
}

interface GuildDetail {
  id: number;
  name: string;
  description: string;
  member_count: number;
  total_bounties: number;
  reputation_score: number;
  created_at: string;
  is_member: boolean;
  members: GuildMember[];
}

export default function GuildDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [guild, setGuild] = useState<GuildDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGuildDetail();
  }, [params.id]);

  const fetchGuildDetail = async () => {
    try {
      const response = await api.get(`/guild/${params.id}`);
      setGuild(response.data);
    } catch (error) {
      console.error("Failed to fetch guild details:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinLeave = async () => {
    try {
      if (guild?.is_member) {
        await api.post(`/guild/${params.id}/leave`);
      } else {
        await api.post(`/guild/${params.id}/join`);
      }
      fetchGuildDetail();
    } catch (error) {
      console.error("Failed to join/leave guild:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
          <p className="text-slate-400 mt-4">Loading guild details...</p>
        </div>
      </div>
    );
  }

  if (!guild) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-400 text-lg">Guild not found</p>
          <button
            onClick={() => router.push("/guilds")}
            className="mt-4 px-6 py-3 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition"
          >
            Back to Guilds
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
            onClick={() => router.push("/guilds")}
            className="flex items-center text-slate-400 hover:text-white mb-6 transition"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Guilds
          </button>

          <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-lg p-8 mb-8">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-start space-x-6">
                <div className="w-20 h-20 bg-gradient-to-br from-gray-500 to-gray-600 rounded-lg flex items-center justify-center text-4xl">
                  
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-white mb-2">{guild.name}</h1>
                  <p className="text-slate-400 max-w-2xl">{guild.description}</p>
                </div>
              </div>
              <button
                onClick={handleJoinLeave}
                className={`px-6 py-3 rounded-lg font-semibold transition ${
                  guild.is_member
                    ? "bg-red-600 hover:bg-red-500 text-white"
                    : "bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-400 hover:to-gray-400 text-white"
                }`}
              >
                {guild.is_member ? "Leave Guild" : "Join Guild"}
              </button>
            </div>

            <div className="grid grid-cols-4 gap-6 pt-6 border-t border-slate-800">
              <div>
                <p className="text-sm text-slate-400 mb-1">Members</p>
                <p className="text-2xl font-bold text-white">{guild.member_count}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Bounties</p>
                <p className="text-2xl font-bold text-yellow-400">${guild.total_bounties.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Reputation</p>
                <p className="text-2xl font-bold text-cyan-400">{guild.reputation_score}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Founded</p>
                <p className="text-lg font-bold text-white">{new Date(guild.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-6">Guild Members</h2>
            
            <div className="space-y-3">
              {guild.members.map((member, index) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition"
                >
                  <div className="flex items-center space-x-4">
                    <span className="text-2xl font-bold text-slate-600">#{index + 1}</span>
                    <div>
                      <p className="text-white font-semibold">{member.username}</p>
                      <p className="text-sm text-slate-400">
                        Joined {new Date(member.joined_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-8 text-sm">
                    <div className="text-center">
                      <p className="text-slate-400">Reputation</p>
                      <p className="text-cyan-400 font-bold">{member.reputation_score}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-slate-400">Bugs Found</p>
                      <p className="text-green-400 font-bold">{member.bugs_found}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-slate-400">Bounties</p>
                      <p className="text-yellow-400 font-bold">${member.bounties_earned.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
