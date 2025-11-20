export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-20">
        <h1 className="text-5xl font-bold mb-6">About Ikodio</h1>
        <div className="prose prose-invert">
          <p className="text-xl text-white/80 leading-relaxed mb-6">
            Ikodio is revolutionizing the bug bounty industry with AI-powered vulnerability detection 
            and a comprehensive marketplace for security researchers.
          </p>
          <p className="text-white/70 leading-relaxed mb-4">
            Founded in 2024, we combine cutting-edge artificial intelligence with decades of 
            cybersecurity expertise to help organizations discover and fix vulnerabilities faster 
            than ever before.
          </p>
          <p className="text-white/70 leading-relaxed">
            Our mission is to make the internet more secure by empowering security researchers 
            and organizations to work together efficiently.
          </p>
        </div>
      </div>
    </div>
  );
}
