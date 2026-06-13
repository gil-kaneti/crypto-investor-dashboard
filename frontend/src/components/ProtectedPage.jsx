import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import LoadingScreen from "./LoadingScreen";

export default function ProtectedPage({ children }) {
  const location = useLocation();
  const { isAuthenticated, isCheckingUser } = useAuth();

  if (isCheckingUser) {
    return <LoadingScreen label="Opening your dashboard" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}
