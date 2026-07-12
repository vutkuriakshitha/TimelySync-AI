// src/pages/Settings.jsx
import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Modal,
  Alert,
} from "react-bootstrap";
import { Bell, Shield, Moon, Globe, Save, AlertTriangle } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import toast from "react-hot-toast";

const Settings = () => {
  const { changePassword, deleteAccount } = useContext(AuthContext);
  const navigate = useNavigate();

  const [settings, setSettings] = useState({
    emailNotifications: localStorage.getItem("pref_emailNotifications") !== "false",
    pushNotifications: localStorage.getItem("pref_pushNotifications") !== "false",
    darkMode: localStorage.getItem("darkMode") === "true",
    language: localStorage.getItem("pref_language") || "en",
    reminderTime: localStorage.getItem("pref_reminderTime") || "1hour",
  });

  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordForm, setPasswordForm] = useState({ currentPassword: "", newPassword: "", confirmPassword: "" });
  const [passwordError, setPasswordError] = useState("");
  const [changingPassword, setChangingPassword] = useState(false);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleSave = () => {
    localStorage.setItem("pref_emailNotifications", String(settings.emailNotifications));
    localStorage.setItem("pref_pushNotifications", String(settings.pushNotifications));
    localStorage.setItem("darkMode", String(settings.darkMode));
    localStorage.setItem("pref_language", settings.language);
    localStorage.setItem("pref_reminderTime", settings.reminderTime);
    document.body.classList.toggle("dark-mode", settings.darkMode);
    toast.success("Settings saved successfully!");
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPasswordError("");

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPasswordError("New passwords do not match");
      return;
    }
    if (passwordForm.newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters");
      return;
    }

    setChangingPassword(true);
    const result = await changePassword(passwordForm.currentPassword, passwordForm.newPassword);
    setChangingPassword(false);
    if (result.success) {
      setShowPasswordModal(false);
      setPasswordForm({ currentPassword: "", newPassword: "", confirmPassword: "" });
    } else {
      setPasswordError(result.error);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleting(true);
    const result = await deleteAccount();
    setDeleting(false);
    if (result.success) {
      navigate("/login");
    }
  };

  return (
    <Container fluid className="py-4">
      <Row>
        <Col lg={8} className="mx-auto">
          <h2 className="mb-4">Settings</h2>

          <Card className="shadow-sm mb-4">
            <Card.Body>
              <h5 className="mb-3 d-flex align-items-center gap-2">
                <Bell size={18} /> Notifications
              </h5>
              <Form>
                <Form.Check
                  type="switch"
                  label="Email Notifications"
                  checked={settings.emailNotifications}
                  onChange={(e) => setSettings({ ...settings, emailNotifications: e.target.checked })}
                  className="mb-3"
                />
                <Form.Check
                  type="switch"
                  label="Push Notifications"
                  checked={settings.pushNotifications}
                  onChange={(e) => setSettings({ ...settings, pushNotifications: e.target.checked })}
                  className="mb-3"
                />
                <Form.Group className="mt-3">
                  <Form.Label>Reminder Time</Form.Label>
                  <Form.Select
                    value={settings.reminderTime}
                    onChange={(e) => setSettings({ ...settings, reminderTime: e.target.value })}
                  >
                    <option value="15min">15 minutes before</option>
                    <option value="30min">30 minutes before</option>
                    <option value="1hour">1 hour before</option>
                    <option value="1day">1 day before</option>
                  </Form.Select>
                </Form.Group>
              </Form>
            </Card.Body>
          </Card>

          <Card className="shadow-sm mb-4">
            <Card.Body>
              <h5 className="mb-3 d-flex align-items-center gap-2">
                <Shield size={18} /> Privacy & Security
              </h5>
              <Button
                variant="outline-primary"
                className="mb-2 w-100"
                onClick={() => setShowPasswordModal(true)}
              >
                Change Password
              </Button>
              <Button
                variant="outline-danger"
                className="w-100"
                onClick={() => setShowDeleteModal(true)}
              >
                Delete Account
              </Button>
            </Card.Body>
          </Card>

          <Card className="shadow-sm">
            <Card.Body>
              <h5 className="mb-3 d-flex align-items-center gap-2">
                <Globe size={18} /> Preferences
              </h5>
              <Form>
                <Form.Check
                  type="switch"
                  label={
                    <span className="d-flex align-items-center gap-1">
                      <Moon size={14} /> Dark Mode
                    </span>
                  }
                  checked={settings.darkMode}
                  onChange={(e) => setSettings({ ...settings, darkMode: e.target.checked })}
                  className="mb-3"
                />
                <Form.Group className="mt-3">
                  <Form.Label>Language</Form.Label>
                  <Form.Select
                    value={settings.language}
                    onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                  </Form.Select>
                </Form.Group>
              </Form>
              <Button variant="primary" className="mt-3 w-100" onClick={handleSave}>
                <Save size={18} className="me-2" />
                Save Settings
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Change Password Modal */}
      <Modal show={showPasswordModal} onHide={() => setShowPasswordModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Change Password</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleChangePassword}>
          <Modal.Body>
            {passwordError && <Alert variant="danger">{passwordError}</Alert>}
            <Form.Group className="mb-3">
              <Form.Label>Current Password</Form.Label>
              <Form.Control
                type="password"
                value={passwordForm.currentPassword}
                onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>New Password</Form.Label>
              <Form.Control
                type="password"
                value={passwordForm.newPassword}
                onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Confirm New Password</Form.Label>
              <Form.Control
                type="password"
                value={passwordForm.confirmPassword}
                onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                required
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowPasswordModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={changingPassword}>
              {changingPassword ? "Updating..." : "Update Password"}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Delete Account Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Delete Account</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="danger" className="mb-0">
            <AlertTriangle className="me-2" />
            This will permanently delete your account and all associated tasks.
            This action cannot be undone.
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteAccount} disabled={deleting}>
            {deleting ? "Deleting..." : "Delete My Account"}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Settings;
