'use client';

import { useState, useEffect } from 'react';
import { SimpleCard } from '@/components/ui/simple-card';
import { SimpleBadge } from '@/components/ui/simple-badge';
import { Button } from '@/components/ui/button';

interface NFTMetadata {
  name: string;
  description: string;
  image: string;
  attributes: {
    trait_type: string;
    value: string | number;
  }[];
}

interface NFT {
  id: number;
  token_id: string;
  bug_id: number;
  owner_id: number;
  owner_username: string;
  metadata: NFTMetadata;
  listed_price: number | null;
  created_at: string;
}

export default function NFTPage() {
  const [nfts, setNfts] = useState<NFT[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'owned' | 'listed'>('all');

  useEffect(() => {
    fetchNFTs();
  }, [filter]);

  const fetchNFTs = async () => {
    try {
      const response = await fetch(`/api/nft?filter=${filter}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setNfts(data);
      }
    } catch (error) {
      console.error('Failed to fetch NFTs:', error);
    } finally {
      setLoading(false);
    }
  };

  const mintNFT = async (bugId: number) => {
    try {
      const response = await fetch('/api/nft/mint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ bug_id: bugId })
      });

      if (response.ok) {
        fetchNFTs();
      }
    } catch (error) {
      console.error('Failed to mint NFT:', error);
    }
  };

  const listForSale = async (nftId: number, price: number) => {
    try {
      const response = await fetch(`/api/nft/${nftId}/list`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ price })
      });

      if (response.ok) {
        fetchNFTs();
      }
    } catch (error) {
      console.error('Failed to list NFT:', error);
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
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Bug NFT Marketplace</h1>
        <p className="text-gray-400">
          Mint, collect, and trade unique NFTs representing your discovered vulnerabilities
        </p>
      </div>

      <div className="flex gap-3 mb-6">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All NFTs
        </Button>
        <Button
          variant={filter === 'owned' ? 'default' : 'outline'}
          onClick={() => setFilter('owned')}
        >
          My Collection
        </Button>
        <Button
          variant={filter === 'listed' ? 'default' : 'outline'}
          onClick={() => setFilter('listed')}
        >
          Listed for Sale
        </Button>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {nfts.map((nft) => (
          <SimpleCard key={nft.id}>
            <div className="aspect-square bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg mb-4 flex items-center justify-center">
              {nft.metadata.image ? (
                <img src={nft.metadata.image} alt={nft.metadata.name} className="w-full h-full object-cover rounded-lg" />
              ) : (
                <div className="text-white text-6xl font-bold">
                  #{nft.token_id.slice(-4)}
                </div>
              )}
            </div>

            <div className="mb-3">
              <h3 className="text-xl font-semibold mb-1">{nft.metadata.name}</h3>
              <p className="text-sm text-gray-400">{nft.metadata.description}</p>
            </div>

            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Attributes</p>
              <div className="flex flex-wrap gap-2">
                {nft.metadata.attributes.map((attr, idx) => (
                  <SimpleBadge key={idx} variant="outline">
                    {attr.trait_type}: {attr.value}
                  </SimpleBadge>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-700 pt-3 mb-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">Owner</span>
                <span className="font-medium">{nft.owner_username}</span>
              </div>
              {nft.listed_price && (
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-gray-500">Price</span>
                  <span className="font-semibold text-green-400">${nft.listed_price}</span>
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <Button size="sm" className="flex-1">View</Button>
              {nft.listed_price ? (
                <Button size="sm" variant="default" className="flex-1">Buy Now</Button>
              ) : (
                <Button size="sm" variant="outline" className="flex-1">Make Offer</Button>
              )}
            </div>
          </SimpleCard>
        ))}

        {nfts.length === 0 && (
          <div className="col-span-full">
            <SimpleCard>
              <p className="text-center text-gray-500 py-8">
                No NFTs found. Discover bugs to mint your first NFT!
              </p>
            </SimpleCard>
          </div>
        )}
      </div>
    </div>
  );
}
