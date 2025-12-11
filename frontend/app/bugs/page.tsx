"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { 
  Bug, Shield, AlertTriangle, CheckCircle, Clock, 
  Plus, Search, DollarSign, ChevronRight
} from "lucide-react";
import { api } from "@/lib/api";

interface BugReport {
  id: number;
  title: string;
  severity: string;
  status: string;
  bounty_amount: number;
  target_url: string;
  created_at: string;
  validated: boolean;
  reporter_name?: string;
  description?: string;
}

// Animated background
function GridBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-radial from-white/5 via-transparent to-transparent rounded-full blur-3xl" />
    </div>
  );
}

// Stats Card Component
function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: string | number; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-white/20 transition-all"
    >
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div>
          <p className="text-gray-400 text-sm">{label}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
      </div>
    </motion.div>
  );
}

// Severity Badge
function SeverityBadge({ severity }: { severity: string }) {
  const config: Record<string, { bg: string; text: string; icon: any }> = {
    critical: { bg: "bg-red-500/20 border-red-500/50", text: "text-red-400", icon: AlertTriangle },
    high: { bg: "bg-orange-500/20 border-orange-500/50", text: "text-orange-400", icon: AlertTriangle },
    medium: { bg: "bg-yellow-500/20 border-yellow-500/50", text: "text-yellow-400", icon: Shield },
    low: { bg: "bg-green-500/20 border-green-500/50", text: "text-green-400", icon: Shield },
  };
  
  const { bg, text, icon: Icon } = config[severity?.toLowerCase()] || config.medium;
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border ${bg} ${text} text-xs font-medium`}>
      <Icon className="w-3 h-3" />
      {severity?.toUpperCase()}
    </span>
  );
}

// Status Badge
function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; icon: any }> = {
    pending: { bg: "bg-gray-500/20 border-gray-500/50", text: "text-gray-400", icon: Clock },
    validated: { bg: "bg-green-500/20 border-green-500/50", text: "text-green-400", icon: CheckCircle },
    fixed: { bg: "bg-white/20 border-white/50", text: "text-white", icon: CheckCircle },
    rejected: { bg: "bg-gray-500/20 border-gray-500/50", text: "text-gray-400", icon: Shield },
  };
  
  const { bg, text, icon: Icon } = config[status?.toLowerCase()] || config.pending;
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border ${bg} ${text} text-xs font-medium`}>
      <Icon className="w-3 h-3" />
      {status?.charAt(0).toUpperCase() + status?.slice(1)}
    </span>
  );
}

// Bug Card Component
function BugCard({ bug, index }: { bug: BugReport; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Link href={`/bugs/${bug.id}`}>
        <div className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-white/30 hover:bg-white/10 transition-all duration-300 cursor-pointer">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-white/10 border border-white/10 flex items-center justify-center">
                  <Bug className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-white group-hover:text-gray-300 transition-colors truncate">
                    {bug.title}
                  </h3>
                  <p className="text-gray-500 text-sm truncate">{bug.target_url}</p>
                </div>
              </div>
              
              {bug.description && (
                <p className="text-gray-400 text-sm line-clamp-2 mb-4">
                  {bug.description}
                </p>
              )}
              
              <div className="flex items-center flex-wrap gap-2">
                <SeverityBadge severity={bug.severity} />
                <StatusBadge status={bug.status} />
                {bug.reporter_name && (
                  <span className="text-gray-500 text-sm">
                    by <span className="text-gray-400">{bug.reporter_name}</span>
                  </span>
                )}
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-3">
              {bug.bounty_amount > 0 && (
                <div className="flex items-center gap-1 text-green-400 font-semibold">
                  <DollarSign className="w-4 h-4" />
                  <span>{bug.bounty_amount.toLocaleString()}</span>
                </div>
              )}
              <span className="text-gray-500 text-xs">
                {new Date(bug.created_at).toLocaleDateString('id-ID', { 
                  day: 'numeric', 
                  month: 'short', 
                  year: 'numeric' 
                })}
              </span>
              <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-white group-hover:translate-x-1 transition-all" />
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

// Filter Button Component
function FilterButton({ 
  active, 
  onClick, 
  children,
  count 
}: { 
  active: boolean; 
  onClick: () => void; 
  children: React.ReactNode;
  count?: number;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
        active
          ? "bg-white text-black"
          : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10"
      }`}
    >
      {children}
      {count !== undefined && count > 0 && (
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          active ? "bg-black/20 text-black" : "bg-white/10 text-gray-400"
        }`}>
          {count}
        </span>
      )}
    </button>
  );
}

export default function BugsPage() {
  const router = useRouter();
  const [bugs, setBugs] = useState<BugReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

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

  const filteredBugs = bugs.filter(bug => 
    bug.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    bug.target_url?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const stats = {
    total: bugs.length,
    pending: bugs.filter(b => b.status === "pending").length,
    validated: bugs.filter(b => b.status === "validated").length,
    totalBounty: bugs.reduce((acc, b) => acc + (b.bounty_amount || 0), 0),
  };

  return (
    <div className="min-h-screen bg-black text-white relative">
      <GridBackground />
      
      <div className="relative z-10">
        {/* Header Section */}
        <div className="border-b border-white/10">
          <div className="container mx-auto px-6 py-12">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col md:flex-row md:items-center md:justify-between gap-6"
            >
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center">
                    <Bug className="w-6 h-6 text-white" />
                  </div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                    Bug Reports
                  </h1>
                </div>
                <p className="text-gray-400 text-lg">
                  Track and manage vulnerability reports from your security researchers
                </p>
              </div>
              
              <Link href="/bugs/new">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-black font-semibold rounded-xl hover:bg-gray-200 transition-all shadow-lg"
                >
                  <Plus className="w-5 h-5" />
                  Report Bug
                </motion.button>
              </Link>
            </motion.div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="container mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <StatCard icon={Bug} label="Total Reports" value={stats.total} color="bg-white/10" />
            <StatCard icon={Clock} label="Pending Review" value={stats.pending} color="bg-white/10" />
            <StatCard icon={CheckCircle} label="Validated" value={stats.validated} color="bg-green-500/20" />
            <StatCard icon={DollarSign} label="Total Bounty" value={`$${stats.totalBounty.toLocaleString()}`} color="bg-yellow-500/20" />
          </div>

          {/* Filters and Search */}
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            <div className="flex flex-wrap gap-2">
              <FilterButton active={filter === "all"} onClick={() => setFilter("all")} count={bugs.length}>
                All
              </FilterButton>
              <FilterButton active={filter === "pending"} onClick={() => setFilter("pending")} count={stats.pending}>
                <Clock className="w-4 h-4" />
                Pending
              </FilterButton>
              <FilterButton active={filter === "validated"} onClick={() => setFilter("validated")} count={stats.validated}>
                <CheckCircle className="w-4 h-4" />
                Validated
              </FilterButton>
              <FilterButton active={filter === "fixed"} onClick={() => setFilter("fixed")}>
                <Shield className="w-4 h-4" />
                Fixed
              </FilterButton>
            </div>
            
            <div className="flex-1 md:max-w-md ml-auto">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search bugs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 focus:ring-1 focus:ring-white/30 transition-all"
                />
              </div>
            </div>
          </div>

          {/* Bug List */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <p className="text-gray-400">Loading bug reports...</p>
              </div>
            </div>
          ) : filteredBugs.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                <Bug className="w-10 h-10 text-gray-600" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">No bugs found</h3>
              <p className="text-gray-500 mb-6">
                {searchQuery 
                  ? "Try adjusting your search query" 
                  : "Be the first to report a vulnerability!"}
              </p>
              <Link href="/bugs/new">
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 border border-white/20 text-white rounded-xl hover:bg-white/20 transition-all">
                  <Plus className="w-5 h-5" />
                  Report First Bug
                </button>
              </Link>
            </motion.div>
          ) : (
            <div className="space-y-4">
              {filteredBugs.map((bug, index) => (
                <BugCard key={bug.id} bug={bug} index={index} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
