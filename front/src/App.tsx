import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import CreatePost from './pages/CreatePost';
import Preview from './pages/Preview';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './context/AuthContext';
import './index.css';

function Navigation() {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const isHome = location.pathname === '/';
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  // No mostrar navegación en la página principal o páginas de auth
  if (isHome || isAuthPage) return null;

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold text-blue-600">
              📱 Social Media Publisher
            </Link>
            {isAuthenticated && (
              <div className="flex space-x-4">
                <Link
                  to="/create"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Crear Post
                </Link>
                <Link
                  to="/dashboard"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
              </div>
            )}
          </div>
          
          {isAuthenticated && (
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Hola, <span className="font-medium">{user?.name}</span>
              </span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
              >
                Cerrar Sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

function AppRoutes() {
  return (
    <>
      <Navigation />
      
      {/* Routes */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/create"
          element={
            <ProtectedRoute>
              <CreatePost />
            </ProtectedRoute>
          }
        />
        <Route
          path="/preview/:postId"
          element={
            <ProtectedRoute>
              <Preview />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <AppRoutes />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
