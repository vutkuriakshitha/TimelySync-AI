// src/components/common/Layout.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";

const Layout = ({ children }) => {
  useKeyboardShortcuts();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth >= 992) setSidebarOpen(false);
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  useEffect(() => {
    document.body.classList.toggle("sidebar-open", sidebarOpen);
    return () => document.body.classList.remove("sidebar-open");
  }, [sidebarOpen]);

  return (
    <div className="app-shell d-flex">
      {sidebarOpen && (
        <button
          type="button"
          className="app-sidebar-backdrop"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <Sidebar open={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />
      <div className="app-main flex-grow-1">
        <Topbar onMenuClick={() => setSidebarOpen((prev) => !prev)} />
        <div className="app-content">{children}</div>
      </div>
    </div>
  );
};

export default Layout;
