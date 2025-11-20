'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';

interface Team {
  id: number;
  name: string;
  description: string;
  member_count: number;
  created_at: string;
  role: string;
  members: TeamMember[];
}

interface TeamMember {
  id: number;
  user_id: number;
  username: string;
  email: string;
  role: string;
  joined_at: string;
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [newTeamDescription, setNewTeamDescription] = useState('');

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const response = await fetch('/api/teams', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setTeams(data);
      }
    } catch (error) {
      console.error('Failed to fetch teams:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTeam = async () => {
    try {
      const response = await fetch('/api/teams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          name: newTeamName,
          description: newTeamDescription
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTeams([...teams, data]);
        setShowCreateModal(false);
        setNewTeamName('');
        setNewTeamDescription('');
      }
    } catch (error) {
      console.error('Failed to create team:', error);
    }
  };

  const inviteMember = async (teamId: number, email: string) => {
    try {
      const response = await fetch(`/api/teams/${teamId}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        fetchTeams();
      }
    } catch (error) {
      console.error('Failed to invite member:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">Teams</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          Create New Team
        </Button>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {teams.map((team) => (
          <SimpleCard key={team.id} onClick={() => setSelectedTeam(team)}>
            <div className="cursor-pointer">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-xl font-semibold">{team.name}</h3>
                <SimpleBadge>{team.role}</SimpleBadge>
              </div>
              
              <p className="text-gray-600 mb-4">{team.description}</p>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">
                  {team.member_count} members
                </span>
                <span className="text-gray-500">
                  Created {new Date(team.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </SimpleCard>
        ))}

        {teams.length === 0 && (
          <div className="col-span-full">
            <SimpleCard>
              <p className="text-center text-gray-600 py-8">
                No teams found. Create one to collaborate with others.
              </p>
            </SimpleCard>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">Create New Team</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Team Name
              </label>
              <input
                type="text"
                value={newTeamName}
                onChange={(e) => setNewTeamName(e.target.value)}
                className="w-full border rounded px-3 py-2"
                placeholder="Security Team"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">
                Description
              </label>
              <textarea
                value={newTeamDescription}
                onChange={(e) => setNewTeamDescription(e.target.value)}
                className="w-full border rounded px-3 py-2"
                rows={3}
                placeholder="Team description..."
              />
            </div>

            <div className="flex gap-3">
              <Button onClick={createTeam} className="flex-1">
                Create
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowCreateModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {selectedTeam && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">{selectedTeam.name}</h2>
            <p className="text-gray-600 mb-6">{selectedTeam.description}</p>

            <h3 className="text-lg font-semibold mb-3">Members</h3>
            <div className="space-y-3 mb-6">
              {selectedTeam.members?.map((member) => (
                <div key={member.id} className="flex justify-between items-center p-3 border rounded">
                  <div>
                    <p className="font-medium">{member.username}</p>
                    <p className="text-sm text-gray-600">{member.email}</p>
                  </div>
                  <SimpleBadge>{member.role}</SimpleBadge>
                </div>
              ))}
            </div>

            <Button onClick={() => setSelectedTeam(null)}>
              Close
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
