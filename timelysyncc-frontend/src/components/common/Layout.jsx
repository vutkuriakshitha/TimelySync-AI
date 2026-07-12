// src/components/common/Layout.jsx
import React from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";

const Layout = ({ children }) => {
  useKeyboardShortcuts();

  return (
    <div className="d-flex">
      <Sidebar />
      <div className="flex-grow-1" style={{ marginLeft: "250px" }}>
        <Topbar />
        <div className="p-4" style={{ marginTop: "60px" }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;
