import { useAuth } from "@/lib/auth";
import { Navigate } from "react-router";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return null; //TODO: replace with a spinner
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return children;
}