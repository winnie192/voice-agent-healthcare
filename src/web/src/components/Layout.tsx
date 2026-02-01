import { Link, Outlet, useNavigate } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/settings', label: 'Settings' },
  { path: '/knowledge-base', label: 'Knowledge Base' },
  { path: '/services', label: 'Services' },
  { path: '/booking-rules', label: 'Booking Rules' },
  { path: '/call-logs', label: 'Call Logs' },
];

export default function Layout() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('businessId');
    navigate('/login');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <span className="text-xl font-bold text-indigo-600">VoiceAgent</span>
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="text-gray-600 hover:text-indigo-600 text-sm font-medium"
              >
                {item.label}
              </Link>
            ))}
          </div>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-500 hover:text-red-600"
          >
            Logout
          </button>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
