// src/components/common/Topbar.jsx
import React, { useContext, useEffect, useRef, useState, useCallback } from "react";
import { Navbar, Container, Nav, Dropdown, Badge, Image, Modal } from "react-bootstrap";
import { Bell, User, LogOut, Settings as SettingsIcon, Users, Moon, Sun, AlertTriangle, Award, Info, Zap, CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";
import notificationService from "../../services/notificationService";
import AccountSwitcher from "../dashboard/AccountSwitcher";
import QuickActions from "../dashboard/QuickActions";

const POLL_MS = Number(process.env.REACT_APP_NOTIFICATIONS_POLL_MS) || 30000;

const notificationIcon = (type) => {
  switch ((type || "").toLowerCase()) {
    case "risk_alert":
    case "overdue":
      return <AlertTriangle size={16} className="text-danger" />;
    case "achievement":
      return <Award size={16} className="text-warning" />;
    case "task_completed":
      return <CheckCircle size={16} className="text-success" />;
    default:
      return <Info size={16} className="text-primary" />;
  }
};

const Topbar = () => {
  const { user, logout, switchAccount, availableAccounts } = useContext(AuthContext);
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showAccountSwitcher, setShowAccountSwitcher] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [darkMode, setDarkMode] = useState(localStorage.getItem("darkMode") === "true");
  const notificationRef = useRef(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const loadNotifications = useCallback(async () => {
    try {
      const response = await notificationService.getNotifications();
      setNotifications(response.data || []);
    } catch (error) {
      console.error("Error loading notifications:", error);
    }
  }, []);

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, POLL_MS);
    return () => clearInterval(interval);
  }, [loadNotifications]);

  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
    localStorage.setItem("darkMode", darkMode ? "true" : "false");
  }, [darkMode]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleMarkAsRead = async (notification) => {
    if (notification.read) return;
    try {
      await notificationService.markAsRead(notification.id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notification.id ? { ...n, read: true } : n)),
      );
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
    }
  };

  const handleLogout = async () => {
    setShowLogoutConfirm(false);
    await logout();
  };

  const handleSwitchAccount = async (accountId) => {
    await switchAccount(accountId);
    setShowAccountSwitcher(false);
  };

  return (
    <>
      {showQuickActions && (
        <div
          className="position-fixed start-0 top-0 h-100 bg-white shadow-lg"
          style={{ width: "300px", zIndex: 1040, marginTop: "60px" }}
        >
          <QuickActions onClose={() => setShowQuickActions(false)} />
        </div>
      )}

      <Navbar
        bg="white"
        className="shadow-sm px-3 position-fixed"
        style={{
          marginLeft: "250px",
          width: "calc(100% - 250px)",
          zIndex: 999,
          top: 0,
          height: "60px",
        }}
      >
        <Container fluid>
          <Navbar.Text className="fw-semibold">
            Welcome back, {user?.name || "User"}! 👋
          </Navbar.Text>
          <Nav className="ms-auto align-items-center gap-2">
            <button
              type="button"
              className="btn btn-outline-primary btn-sm"
              onClick={() => setShowQuickActions((prev) => !prev)}
              title="Quick Actions"
            >
              <Zap size={16} />
            </button>

            <button
              type="button"
              className="btn btn-outline-secondary btn-sm"
              onClick={() => setDarkMode((prev) => !prev)}
              title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {darkMode ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            <div ref={notificationRef} className="position-relative">
              <button
                type="button"
                className="btn btn-outline-secondary btn-sm position-relative"
                onClick={() => setShowNotifications((prev) => !prev)}
              >
                <Bell size={16} />
                {unreadCount > 0 && (
                  <Badge
                    bg="danger"
                    pill
                    className="position-absolute top-0 start-100 translate-middle"
                  >
                    {unreadCount}
                  </Badge>
                )}
              </button>

              {showNotifications && (
                <div
                  className="position-absolute end-0 mt-2 bg-white shadow-lg rounded border"
                  style={{ width: "340px", zIndex: 1050 }}
                >
                  <div className="d-flex justify-content-between align-items-center p-3 border-bottom">
                    <span className="fw-semibold">Notifications</span>
                    {unreadCount > 0 && (
                      <button
                        className="btn btn-link btn-sm p-0"
                        onClick={handleMarkAllRead}
                      >
                        Mark all as read
                      </button>
                    )}
                  </div>
                  <div style={{ maxHeight: "380px", overflowY: "auto" }}>
                    {notifications.length > 0 ? (
                      notifications.map((notification) => (
                        <div
                          key={notification.id}
                          className={`p-3 border-bottom ${!notification.read ? "bg-light" : ""}`}
                          onClick={() => handleMarkAsRead(notification)}
                          style={{ cursor: "pointer" }}
                        >
                          <div className="d-flex gap-2">
                            <div className="flex-shrink-0">{notificationIcon(notification.type)}</div>
                            <div className="flex-grow-1">
                              <p className="mb-1 small">{notification.message}</p>
                              <small className="text-muted">
                                {notification.createdAt
                                  ? new Date(notification.createdAt).toLocaleString()
                                  : ""}
                              </small>
                            </div>
                            {!notification.read && (
                              <span
                                className="align-self-center bg-primary rounded-circle flex-shrink-0"
                                style={{ width: 8, height: 8 }}
                              />
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4 text-muted">
                        <Bell size={28} className="mb-2" />
                        <p className="small mb-0">No notifications yet</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <Dropdown align="end">
              <Dropdown.Toggle
                variant="link"
                bsPrefix="p-0"
                className="text-dark d-flex align-items-center gap-2 text-decoration-none"
              >
                <Image
                  src={
                    user?.avatar ||
                    `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || "U")}&background=0D6EFD&color=fff`
                  }
                  roundedCircle
                  width="32"
                  height="32"
                />
                <span className="d-none d-md-block">{user?.name?.split(" ")[0]}</span>
              </Dropdown.Toggle>
              <Dropdown.Menu align="end">
                <Dropdown.Header>{user?.email || ""}</Dropdown.Header>
                <Dropdown.Item onClick={() => navigate("/profile")}>
                  <User size={14} className="me-2" /> Profile
                </Dropdown.Item>
                <Dropdown.Item onClick={() => setShowAccountSwitcher(true)}>
                  <Users size={14} className="me-2" /> Switch Account
                </Dropdown.Item>
                <Dropdown.Item onClick={() => navigate("/settings")}>
                  <SettingsIcon size={14} className="me-2" /> Settings
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item onClick={() => setShowLogoutConfirm(true)} className="text-danger">
                  <LogOut size={14} className="me-2" /> Logout
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </Nav>
        </Container>
      </Navbar>

      <Modal show={showLogoutConfirm} onHide={() => setShowLogoutConfirm(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Logout</Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center py-3">
          <LogOut size={48} className="text-danger mb-3" />
          <h5>Ready to leave?</h5>
          <p className="text-muted">You'll need to log in again to access your tasks and dashboard.</p>
        </Modal.Body>
        <Modal.Footer>
          <button className="btn btn-secondary" onClick={() => setShowLogoutConfirm(false)}>
            Stay Logged In
          </button>
          <button className="btn btn-danger" onClick={handleLogout}>
            Logout
          </button>
        </Modal.Footer>
      </Modal>

      <Modal show={showAccountSwitcher} onHide={() => setShowAccountSwitcher(false)} centered size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Switch Account</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <AccountSwitcher
            accounts={availableAccounts}
            currentAccount={user}
            onSwitch={handleSwitchAccount}
          />
        </Modal.Body>
      </Modal>
    </>
  );
};

export default Topbar;
