// src/components/common/Sidebar.jsx
import React from "react";
import { Nav } from "react-bootstrap";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  BookOpen,
  Briefcase,
  Trophy,
  Calendar,
  Clock,
  BarChart3,
  Settings,
  User,
} from "lucide-react";

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { path: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { path: "/academic", icon: BookOpen, label: "Academic Planner" },
    { path: "/opportunities", icon: Briefcase, label: "Opportunities" },
    { path: "/goals", icon: Trophy, label: "Personal Goals" },
    { path: "/events", icon: Calendar, label: "Events" },
    { path: "/today", icon: Clock, label: "Today Snapshot" },
    { path: "/accountability", icon: BarChart3, label: "Accountability" },
  ];

  return (
    <div
      className="bg-dark text-white vh-100 position-fixed"
      style={{ width: "250px", overflowY: "auto" }}
    >
      <div className="p-4 border-bottom border-secondary">
        <h4 className="text-primary mb-0">TimelySync</h4>
        <small className="text-muted">Smart Deadline Manager</small>
      </div>
      <Nav className="flex-column p-3">
        {menuItems.map((item) => (
          <Nav.Link
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`text-white mb-2 ${location.pathname === item.path ? "bg-primary" : ""}`}
            style={{
              cursor: "pointer",
              borderRadius: "8px",
              padding: "10px 15px",
            }}
          >
            <item.icon size={18} className="me-3" />
            {item.label}
          </Nav.Link>
        ))}
        <hr className="bg-secondary my-3" />
        <Nav.Link
          onClick={() => navigate("/profile")}
          className="text-white mb-2"
          style={{
            cursor: "pointer",
            borderRadius: "8px",
            padding: "10px 15px",
          }}
        >
          <User size={18} className="me-3" />
          Profile
        </Nav.Link>
        <Nav.Link
          onClick={() => navigate("/settings")}
          className="text-white"
          style={{
            cursor: "pointer",
            borderRadius: "8px",
            padding: "10px 15px",
          }}
        >
          <Settings size={18} className="me-3" />
          Settings
        </Nav.Link>
      </Nav>
    </div>
  );
};

export default Sidebar;
