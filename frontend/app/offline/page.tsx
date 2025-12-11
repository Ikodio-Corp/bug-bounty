export default function OfflinePage() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <svg
            className="mx-auto h-24 w-24 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3"
            />
          </svg>
        </div>
        
        <h1 className="text-3xl font-bold text-white mb-4">
          You're Offline
        </h1>
        
        <p className="text-gray-400 mb-8">
          It looks like you've lost your internet connection. 
          Don't worry, some features are still available offline.
        </p>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-6 text-left">
          <h2 className="text-lg font-semibold text-white mb-3">
            Available Offline:
          </h2>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              View cached bugs and scans
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Access your dashboard
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Draft new bug reports
            </li>
          </ul>
        </div>
        
        <div className="text-sm text-gray-500 mb-6">
          Your changes will sync automatically when you're back online.
        </div>
        
        <button
          onClick={() => window.location.reload()}
          className="w-full bg-white hover:bg-gray-200 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          Try Again
        </button>
        
        <div className="mt-6">
          <a
            href="/"
            className="text-gray-400 hover:text-gray-300 transition-colors"
          >
            Go to Homepage
          </a>
        </div>
      </div>
    </div>
  );
}
