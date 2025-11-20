export default function DocumentationPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      <div className="max-w-6xl mx-auto px-4 py-20">
        <h1 className="text-5xl font-bold mb-6">Documentation</h1>
        <p className="text-xl text-white/80 mb-12">
          Complete guide to using Ikodio Bug Bounty Platform
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/8 transition-colors">
            <h3 className="text-2xl font-bold mb-3">Getting Started</h3>
            <p className="text-white/70 mb-4">Learn the basics of bug hunting with Ikodio</p>
            <ul className="space-y-2 text-white/60">
              <li>• Account setup</li>
              <li>• First scan</li>
              <li>• Understanding reports</li>
            </ul>
          </div>
          
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/8 transition-colors">
            <h3 className="text-2xl font-bold mb-3">API Reference</h3>
            <p className="text-white/70 mb-4">Complete API documentation</p>
            <ul className="space-y-2 text-white/60">
              <li>• Authentication</li>
              <li>• Endpoints</li>
              <li>• Code examples</li>
            </ul>
          </div>
          
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/8 transition-colors">
            <h3 className="text-2xl font-bold mb-3">Integrations</h3>
            <p className="text-white/70 mb-4">Connect with your tools</p>
            <ul className="space-y-2 text-white/60">
              <li>• Slack integration</li>
              <li>• Jira integration</li>
              <li>• Webhook setup</li>
            </ul>
          </div>
          
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/8 transition-colors">
            <h3 className="text-2xl font-bold mb-3">Best Practices</h3>
            <p className="text-white/70 mb-4">Maximize your bug hunting success</p>
            <ul className="space-y-2 text-white/60">
              <li>• Scan optimization</li>
              <li>• Report writing</li>
              <li>• Bug marketplace tips</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
