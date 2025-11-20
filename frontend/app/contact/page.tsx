export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      <div className="max-w-2xl mx-auto px-4 py-20">
        <h1 className="text-5xl font-bold mb-6">Contact Us</h1>
        <p className="text-xl text-white/80 mb-12">
          Get in touch with our team for support, partnerships, or inquiries.
        </p>
        
        <div className="space-y-6 mb-12">
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-bold mb-2">Email</h3>
            <p className="text-white/70">support@ikodio.com</p>
          </div>
          
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-bold mb-2">Sales</h3>
            <p className="text-white/70">sales@ikodio.com</p>
          </div>
          
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-bold mb-2">Support</h3>
            <p className="text-white/70">Available 24/7 via dashboard</p>
          </div>
        </div>
      </div>
    </div>
  );
}
