// src/App.js
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./context/AuthContext";
import { TaskProvider } from "./context/TaskContext";
import ErrorBoundary from "./components/common/ErrorBoundary";
import ProtectedRoute from "./components/common/ProtectedRoute";
import Layout from "./components/common/Layout";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import CreateTask from "./pages/CreateTask";
import TaskDetail from "./pages/TaskDetail";
import AcademicPlanner from "./pages/AcademicPlanner";
import Opportunities from "./pages/Opportunities";
import PersonalGoals from "./pages/PersonalGoals";
import Events from "./pages/Events";
import TodaySnapshot from "./pages/TodaySnapshot";
import Accountability from "./pages/Accountability";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import "./index.css";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <TaskProvider>
            <Toaster position="top-right" />
            <Routes>
              {/* Public Auth Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />

              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/create-task"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <CreateTask />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/task/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <TaskDetail />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/academic"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <AcademicPlanner />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/opportunities"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Opportunities />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/goals"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <PersonalGoals />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/events"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Events />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/today"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <TodaySnapshot />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/accountability"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Accountability />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Profile />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/settings"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Settings />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route path="/404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
          </TaskProvider>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
