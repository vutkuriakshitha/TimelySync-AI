// src/pages/ResetPassword.jsx
import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Container, Card, Form, Button, Alert, Spinner } from "react-bootstrap";
import { Lock, KeyRound } from "lucide-react";
import authService from "../services/authService";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!token) {
      setError("This reset link is invalid or missing a token.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    try {
      await authService.resetPassword(token, password);
      setSuccess(true);
      setTimeout(() => navigate("/login"), 2500);
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "This reset link is invalid or has expired.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-gradient-primary">
      <Container className="d-flex justify-content-center">
        <Card className="shadow-lg border-0" style={{ width: "100%", maxWidth: "450px" }}>
          <Card.Body className="p-5">
            <div className="text-center mb-4">
              <div className="bg-primary text-white rounded-circle d-inline-flex p-3 mb-3">
                <KeyRound size={32} />
              </div>
              <h2 className="fw-bold">Reset Password</h2>
              <p className="text-muted">Choose a new password for your account</p>
            </div>

            {error && (
              <Alert variant="danger" className="py-2 small">
                {error}
              </Alert>
            )}

            {success ? (
              <Alert variant="success">
                Password reset successfully. Redirecting you to sign in...
              </Alert>
            ) : (
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3" controlId="password">
                  <Form.Label>New Password</Form.Label>
                  <div className="position-relative">
                    <Lock
                      size={18}
                      className="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"
                    />
                    <Form.Control
                      type="password"
                      placeholder="Enter new password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="ps-5 py-2"
                      required
                    />
                  </div>
                </Form.Group>

                <Form.Group className="mb-4" controlId="confirmPassword">
                  <Form.Label>Confirm New Password</Form.Label>
                  <div className="position-relative">
                    <Lock
                      size={18}
                      className="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"
                    />
                    <Form.Control
                      type="password"
                      placeholder="Confirm new password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="ps-5 py-2"
                      required
                    />
                  </div>
                </Form.Group>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-100 py-2 fw-semibold d-flex align-items-center justify-content-center gap-2"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Spinner size="sm" animation="border" /> Resetting...
                    </>
                  ) : (
                    "Reset Password"
                  )}
                </Button>
              </Form>
            )}

            <div className="text-center mt-4">
              <Link to="/login" className="text-primary fw-bold text-decoration-none small">
                Back to Sign In
              </Link>
            </div>
          </Card.Body>
        </Card>
      </Container>
    </div>
  );
};

export default ResetPassword;
