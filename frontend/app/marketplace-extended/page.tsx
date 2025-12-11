"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface Listing {
  listing_id: number
  bug_id: number
  listing_price: number
  instant_payment_percentage: number
  status: string
  listed_at: string
}

interface Future {
  future_id: number
  contract_name: string
  target_company: string
  vulnerability_type: string
  contract_price: number
  expiration_date: string
  total_contracts_traded: number
}

export default function MarketplacePage() {
  const [activeTab, setActiveTab] = useState<'listings' | 'futures'>('listings')
  const [listings, setListings] = useState<Listing[]>([])
  const [futures, setFutures] = useState<Future[]>([])
  const [loading, setLoading] = useState(false)

  const loadListings = async () => {
    try {
      const response = await fetch('/api/marketplace/listings?status=active')
      const data = await response.json()
      setListings(data.data || [])
    } catch (error) {
      console.error('Error loading listings:', error)
    }
  }

  const loadFutures = async () => {
    try {
      const response = await fetch('/api/marketplace/futures?status=active')
      const data = await response.json()
      setFutures(data.data || [])
    } catch (error) {
      console.error('Error loading futures:', error)
    }
  }

  const buyListing = async (listingId: number) => {
    if (!confirm('Purchase this bug? 80% payment goes instantly to seller.')) return
    
    setLoading(true)
    try {
      const response = await fetch(`/api/marketplace/listings/${listingId}/buy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ payment_method: 'stripe' })
      })
      const data = await response.json()
      if (data.success) {
        alert('Purchase successful!')
        loadListings()
      }
    } catch (error) {
      console.error('Error buying listing:', error)
    }
    setLoading(false)
  }

  const buyFuturePosition = async (futureId: number) => {
    const quantity = prompt('Enter quantity:')
    if (!quantity) return

    const positionType = confirm('Click OK for LONG, Cancel for SHORT') ? 'long' : 'short'

    setLoading(true)
    try {
      const response = await fetch(`/api/marketplace/futures/${futureId}/buy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          quantity: parseInt(quantity),
          position_type: positionType
        })
      })
      const data = await response.json()
      if (data.success) {
        alert(`${positionType.toUpperCase()} position opened successfully!`)
      }
    } catch (error) {
      console.error('Error buying position:', error)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadListings()
    loadFutures()
  }, [])

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Bug Marketplace & Futures</h1>

      <div className="flex gap-4 mb-6">
        <Button
          onClick={() => setActiveTab('listings')}
          variant={activeTab === 'listings' ? 'default' : 'outline'}
        >
          Bug Listings
        </Button>
        <Button
          onClick={() => setActiveTab('futures')}
          variant={activeTab === 'futures' ? 'default' : 'outline'}
        >
          Bug Futures
        </Button>
      </div>

      {activeTab === 'listings' && (
        <div>
          <div className="bg-gray-800 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">How Bug Trading Works</h3>
            <ul className="text-sm space-y-1">
              <li>80% instant payment to seller when you buy</li>
              <li>10% platform fee</li>
              <li>Acquire bug rights for resale or exploitation analysis</li>
            </ul>
          </div>

          {listings.length === 0 ? (
            <p className="text-gray-500">No active listings</p>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {listings.map((listing) => (
                <div key={listing.listing_id} className="bg-white p-6 rounded-lg shadow">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-semibold">Bug #{listing.bug_id}</h3>
                      <p className="text-sm text-gray-600">Listed {new Date(listing.listed_at).toLocaleDateString()}</p>
                    </div>
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                      {listing.status}
                    </span>
                  </div>

                  <div className="mb-4">
                    <div className="text-2xl font-bold text-white mb-1">
                      ${listing.listing_price.toLocaleString()}
                    </div>
                    <p className="text-xs text-gray-600">
                      Seller gets ${(listing.listing_price * listing.instant_payment_percentage / 100).toLocaleString()} instantly (80%)
                    </p>
                  </div>

                  <Button
                    onClick={() => buyListing(listing.listing_id)}
                    disabled={loading}
                    className="w-full"
                  >
                    Buy Now
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'futures' && (
        <div>
          <div className="bg-gray-800 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">Bug Futures Trading</h3>
            <ul className="text-sm space-y-1">
              <li>Speculate on future bug discoveries</li>
              <li>Go LONG if you believe the bug will be found</li>
              <li>Go SHORT if you believe it won't</li>
              <li>Settles at expiration based on outcome</li>
            </ul>
          </div>

          {futures.length === 0 ? (
            <p className="text-gray-500">No active futures contracts</p>
          ) : (
            <div className="grid md:grid-cols-2 gap-6">
              {futures.map((future) => (
                <div key={future.future_id} className="bg-white p-6 rounded-lg shadow">
                  <h3 className="font-semibold text-lg mb-2">{future.contract_name}</h3>
                  
                  <div className="space-y-2 text-sm mb-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Target:</span>
                      <span className="font-semibold">{future.target_company}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="font-semibold">{future.vulnerability_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Expires:</span>
                      <span className="font-semibold">{new Date(future.expiration_date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Traded:</span>
                      <span className="font-semibold">{future.total_contracts_traded} contracts</span>
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="text-2xl font-bold text-white">
                      ${future.contract_price.toLocaleString()}
                    </div>
                    <p className="text-xs text-gray-600">per contract</p>
                  </div>

                  <Button
                    onClick={() => buyFuturePosition(future.future_id)}
                    disabled={loading}
                    className="w-full"
                  >
                    Trade (Long/Short)
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
