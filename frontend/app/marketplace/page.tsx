'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'
import { Search, Package, Eye, Star, Check, TrendingUp, Award, ShoppingCart, Zap, Shield, FileText, ArrowRight, Sparkles } from 'lucide-react'
import { api } from '@/lib/api'

interface MarketplaceListing {
  id: number
  title: string
  description: string
  price: number
  listing_type: string
  seller_name: string
  seller_reputation?: number
  views: number
  sales_count?: number
  rating?: number
}

const categories = [
  { id: 'all', name: 'All', icon: Package },
  { id: 'tool', name: 'Tools', icon: Shield },
  { id: 'report', name: 'Reports', icon: FileText },
  { id: 'nft', name: 'NFTs', icon: Zap },
  { id: 'subscription', name: 'Subscriptions', icon: TrendingUp }
]

// Floating particles component
const FloatingParticles = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-white rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.5, 0.2],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}
    </div>
  )
}

export default function MarketplacePage() {
  const [listings, setListings] = useState<MarketplaceListing[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState('popular')
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll()
  const smoothProgress = useSpring(scrollYProgress, { stiffness: 100, damping: 30 })
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useEffect(() => {
    fetchListings()
  }, [filter])

  const fetchListings = async () => {
    try {
      const response = await api.get('/marketplace', {
        params: filter !== 'all' ? { category: filter } : {}
      })
      setListings(response.data || [])
    } catch (error) {
      console.error('Failed to fetch listings:', error)
      setListings([])
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = async (listingId: number, title: string) => {
    if (confirm(`Purchase "${title}"?`)) {
      try {
        await api.post('/marketplace/purchase', { listing_id: listingId })
        alert('Purchase successful!')
        fetchListings()
      } catch (error: any) {
        alert(error.response?.data?.detail || 'Purchase failed. Please try again.')
      }
    }
  }

  const filteredListings = listings.filter(listing =>
    listing.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    listing.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900 via-black to-black" />
        <FloatingParticles />
        <motion.div 
          className="relative z-10"
          animate={{ 
            rotate: 360,
            scale: [1, 1.2, 1]
          }}
          transition={{ 
            rotate: { duration: 2, repeat: Infinity, ease: 'linear' },
            scale: { duration: 1.5, repeat: Infinity }
          }}
        >
          <div className="w-16 h-16 border-2 border-white/20 border-t-white" />
        </motion.div>
      </div>
    )
  }

  return (
    <div ref={containerRef} className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Background layers */}
      <div className="fixed inset-0 z-0">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-black to-black" />
        
        {/* Grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem]" />
        
        {/* Floating particles */}
        <FloatingParticles />
        
        {/* Mouse follower light */}
        <motion.div
          className="absolute w-[600px] h-[600px] rounded-full bg-white/5 blur-[100px]"
          animate={{
            x: mousePosition.x - 300,
            y: mousePosition.y - 300,
          }}
          transition={{ type: 'spring', stiffness: 50, damping: 30 }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <div className="relative border-b border-white/5">
          <div className="max-w-7xl mx-auto px-6 py-20">
            {/* Animated background glow */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-b from-white/10 via-transparent to-transparent"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1 }}
            />

            <div className="relative">
              {/* Title */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="text-center mb-6"
              >
                <h1 className="text-7xl font-bold tracking-tight mb-6 leading-tight">
                  <span className="inline-block">
                    <motion.span
                      className="inline-block"
                      whileHover={{ scale: 1.05 }}
                      transition={{ type: 'spring', stiffness: 300 }}
                    >
                      Security
                    </motion.span>
                  </span>{' '}
                  <span className="inline-block bg-gradient-to-r from-white via-gray-400 to-white bg-clip-text text-transparent">
                    Marketplace
                  </span>
                </h1>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed"
                >
                  Discover premium tools, reports, and resources from top security researchers worldwide
                </motion.p>
              </motion.div>

              {/* Search Bar */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="max-w-4xl mx-auto mb-10"
              >
                <div className="relative group">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-white/20 via-white/10 to-white/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500" />
                  <div className="relative flex gap-4">
                    <div className="flex-1 relative">
                      <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="text"
                        placeholder="Search for security tools, reports, NFTs..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-14 pr-6 py-5 bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-white/30 transition-all backdrop-blur-xl rounded-2xl"
                      />
                    </div>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="px-8 py-5 bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-all backdrop-blur-xl rounded-2xl cursor-pointer"
                    >
                      <option value="popular" className="bg-black">Most Popular</option>
                      <option value="recent" className="bg-black">Recently Added</option>
                      <option value="price-low" className="bg-black">Price: Low to High</option>
                      <option value="price-high" className="bg-black">Price: High to Low</option>
                    </select>
                  </div>
                </div>
              </motion.div>

              {/* Categories */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
                className="flex gap-4 overflow-x-auto pb-4 justify-center scrollbar-hide"
              >
                {categories.map((category, index) => {
                  const Icon = category.icon
                  const isActive = filter === category.id
                  return (
                    <motion.button
                      key={category.id}
                      onClick={() => setFilter(category.id)}
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                      className={`relative px-8 py-4 font-medium transition-all flex items-center gap-3 whitespace-nowrap backdrop-blur-xl rounded-full ${
                        isActive
                          ? 'bg-white text-black shadow-lg shadow-white/20'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
                      }`}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="activeCategory"
                          className="absolute inset-0 bg-white rounded-full"
                          style={{ zIndex: -1 }}
                          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        />
                      )}
                      <Icon className="w-5 h-5" />
                      <span>{category.name}</span>
                    </motion.button>
                  )
                })}
              </motion.div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="max-w-7xl mx-auto px-6 py-16">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="grid grid-cols-4 gap-6 mb-20"
          >
            {[
              { label: 'Active Listings', value: filteredListings.length, icon: Package },
              { label: 'Total Sales', value: '2.4k', icon: TrendingUp },
              { label: 'Satisfaction', value: '98%', icon: Star },
              { label: 'Avg Rating', value: '4.8', icon: Award }
            ].map((stat, index) => {
              const Icon = stat.icon
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5, scale: 1.02 }}
                  className="relative group"
                >
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-white/20 to-white/5 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500" />
                  <div className="relative bg-white/5 border border-white/10 p-8 backdrop-blur-xl rounded-2xl">
                    <Icon className="w-8 h-8 text-gray-400 mb-4" />
                    <div className="text-5xl font-bold mb-2">{stat.value}</div>
                    <div className="text-sm text-gray-400 uppercase tracking-wider">{stat.label}</div>
                  </div>
                </motion.div>
              )
            })}
          </motion.div>

          {/* Listings Grid */}
          {filteredListings.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="text-center py-32"
            >
              <motion.div
                animate={{ 
                  y: [0, -10, 0],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ duration: 3, repeat: Infinity }}
                className="inline-flex items-center justify-center w-32 h-32 bg-white/5 border border-white/10 backdrop-blur-xl rounded-3xl mb-8"
              >
                <Package className="w-16 h-16 text-gray-500" />
              </motion.div>
              <h3 className="text-4xl font-bold mb-6">No listings found</h3>
              <p className="text-gray-400 text-lg mb-10 max-w-md mx-auto leading-relaxed">
                Be the first to list a product in this category and start earning
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => window.location.href = '/marketplace/new'}
                className="inline-flex items-center gap-3 px-10 py-5 bg-white text-black font-semibold hover:bg-gray-100 transition-colors rounded-full"
              >
                <span>Create First Listing</span>
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </motion.div>
          ) : (
            <div className="grid grid-cols-3 gap-8">
              {filteredListings.map((listing, index) => (
                <motion.div
                  key={listing.id}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.5, delay: index * 0.05 }}
                  className="group relative"
                >
                  {/* Card glow effect */}
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-white/20 via-white/10 to-white/5 rounded-3xl blur opacity-0 group-hover:opacity-100 transition duration-500" />
                  
                  <motion.div
                    whileHover={{ y: -8 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    className="relative bg-white/5 border border-white/10 backdrop-blur-xl overflow-hidden rounded-3xl"
                  >
                    {/* Image Section */}
                    <div className="relative aspect-video bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center overflow-hidden">
                      {/* Animated background */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-white/10"
                        animate={{
                          rotate: [0, 360],
                          scale: [1, 1.2, 1]
                        }}
                        transition={{
                          duration: 10,
                          repeat: Infinity,
                          ease: 'linear'
                        }}
                      />
                      
                      <motion.div
                        whileHover={{ scale: 1.1, rotate: 10 }}
                        transition={{ type: 'spring', stiffness: 300 }}
                        className="relative z-10"
                      >
                        <Package className="w-24 h-24 text-gray-600" />
                      </motion.div>

                      {listing.sales_count && listing.sales_count > 0 && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute top-6 right-6 px-4 py-2 bg-white/90 backdrop-blur-xl text-black text-sm font-bold rounded-full shadow-lg"
                        >
                          {listing.sales_count} sold
                        </motion.div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="p-8">
                      <div className="flex items-start justify-between mb-4">
                        <h3 className="font-bold text-2xl leading-tight group-hover:text-gray-300 transition-colors">
                          {listing.title}
                        </h3>
                        <span className="px-4 py-1.5 bg-white/10 text-gray-400 text-xs font-bold uppercase tracking-wider whitespace-nowrap ml-4 rounded-full">
                          {listing.listing_type}
                        </span>
                      </div>

                      <p className="text-gray-400 mb-8 line-clamp-2 leading-relaxed">
                        {listing.description}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center gap-6 mb-8 text-sm text-gray-500">
                        <motion.div whileHover={{ scale: 1.1 }} className="flex items-center gap-2">
                          <Eye className="w-4 h-4" />
                          <span>{listing.views || 0}</span>
                        </motion.div>
                        {listing.rating && (
                          <motion.div whileHover={{ scale: 1.1 }} className="flex items-center gap-2">
                            <Star className="w-4 h-4 text-gray-400 fill-gray-400" />
                            <span>{listing.rating.toFixed(1)}</span>
                          </motion.div>
                        )}
                        <motion.div whileHover={{ scale: 1.1 }} className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-gray-400" />
                          <span>Verified</span>
                        </motion.div>
                      </div>

                      {/* Seller */}
                      <div className="flex items-center gap-3 mb-8 pb-8 border-b border-white/10">
                        <div className="w-12 h-12 bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-xl flex items-center justify-center text-sm font-bold rounded-full">
                          {listing.seller_name?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div>
                          <div className="text-gray-500 text-xs mb-1">Seller</div>
                          <div className="font-semibold">{listing.seller_name || 'Anonymous'}</div>
                        </div>
                      </div>

                      {/* Price & Action */}
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Price</div>
                          <div className="text-4xl font-bold">${listing.price.toLocaleString()}</div>
                        </div>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => handlePurchase(listing.id, listing.title)}
                          className="inline-flex items-center gap-3 px-8 py-4 bg-white text-black font-semibold hover:bg-gray-100 transition-colors rounded-full shadow-lg"
                        >
                          <ShoppingCart className="w-5 h-5" />
                          <span>Buy</span>
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              ))}
            </div>
          )}

          {/* CTA Section */}
          {filteredListings.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="mt-32 relative"
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-white/20 via-white/10 to-white/20 rounded-3xl blur-xl" />
              <div className="relative border border-white/10 p-20 text-center backdrop-blur-xl bg-white/5 rounded-3xl overflow-hidden">
                {/* Background animation */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent"
                  animate={{
                    rotate: [0, 360],
                  }}
                  transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: 'linear'
                  }}
                />

                <div className="relative z-10 max-w-3xl mx-auto">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    className="inline-block mb-8"
                  >
                    <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/10 border border-white/20 backdrop-blur-xl rounded-full">
                      <Sparkles className="w-5 h-5 text-white" />
                      <span className="text-sm text-gray-300 font-medium">Join Our Community</span>
                    </div>
                  </motion.div>

                  <h3 className="text-5xl font-bold mb-6">Become a Seller</h3>
                  <p className="text-gray-400 text-xl mb-12 leading-relaxed">
                    List your security tools and earn from your expertise. Join 1,000+ verified sellers
                    and reach thousands of security professionals worldwide.
                  </p>

                  <div className="flex gap-6 justify-center">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => window.location.href = '/marketplace/seller'}
                      className="inline-flex items-center gap-3 px-10 py-5 bg-white text-black font-semibold hover:bg-gray-100 transition-colors rounded-full shadow-2xl"
                    >
                      <span>Get Started</span>
                      <ArrowRight className="w-5 h-5" />
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => window.location.href = '/marketplace/new'}
                      className="inline-flex items-center gap-3 px-10 py-5 bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 transition-colors backdrop-blur-xl rounded-full"
                    >
                      <Package className="w-5 h-5" />
                      <span>Create Listing</span>
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
