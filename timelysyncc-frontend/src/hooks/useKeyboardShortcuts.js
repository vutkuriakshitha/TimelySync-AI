import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const useKeyboardShortcuts = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyPress = (e) => {
      // Ctrl/Cmd + N - New Task
      if ((e.ctrlKey || e.metaKey) && e.key === "n") {
        e.preventDefault();
        navigate("/create-task");
      }
      // Ctrl/Cmd + D - Dashboard
      if ((e.ctrlKey || e.metaKey) && e.key === "d") {
        e.preventDefault();
        navigate("/dashboard");
      }
      // Ctrl/Cmd + / - Help
      if ((e.ctrlKey || e.metaKey) && e.key === "/") {
        e.preventDefault();
        alert(
          "Shortcuts:\nCtrl+N: New Task\nCtrl+D: Dashboard\nCtrl+S: Settings\nEsc: Close modals",
        );
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [navigate]);
};
