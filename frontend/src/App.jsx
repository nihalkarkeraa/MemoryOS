import { Toaster } from "@/components/ui/toaster"
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import PageNotFound from './lib/PageNotFound';
import { AuthProvider, useAuth } from '@/lib/AuthContext';
import UserNotRegisteredError from '@/components/UserNotRegisteredError';
import ScrollToTop from './components/ScrollToTop';
import { Navigate } from 'react-router-dom';
import AppShell from '@/components/layout/AppShell';
import Home from '@/pages/Home';
import Documents from '@/pages/Documents';
import Search from '@/pages/Search';
import Compare from '@/pages/Compare';
import Summaries from '@/pages/Summaries';
import DocumentDetail from '@/pages/DocumentDetail';
import DocumentSummary from '@/pages/DocumentSummary';
// Add page imports here

const AuthenticatedApp = () => {
  const { isLoadingAuth, isLoadingPublicSettings, authError, navigateToLogin } = useAuth();

  // Show loading spinner while checking app public settings or auth
  if (isLoadingPublicSettings || isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin"></div>
      </div>
    );
  }

  // Handle authentication errors
  if (authError) {
    if (authError.type === 'user_not_registered') {
      return <UserNotRegisteredError />;
    } else if (authError.type === 'auth_required') {
      // Redirect to login automatically
      navigateToLogin();
      return null;
    }
  }

  // Render the main app
  return (
    <Routes>
      {/* Add your page Route elements here */}
      <Route element={<AppShell />}>
        <Route path="/home" element={<Home />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/search" element={<Search />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/summaries" element={<Summaries />} />
        <Route path="/documents/:id" element={<DocumentDetail />} />
        <Route path="/documents/:id/summary" element={<DocumentSummary />} />
        <Route path="/" element={<Navigate to="/home" replace />} />
      </Route>
      <Route path="*" element={<PageNotFound />} />
    </Routes>
  );
};


function App() {

  return (
    <AuthProvider>
      <QueryClientProvider client={queryClientInstance}>
        <Router>
          <ScrollToTop />
          <AuthenticatedApp />
        </Router>
        <Toaster />
      </QueryClientProvider>
    </AuthProvider>
  )
}

export default App