// src/pages/ForgotPassword.jsx
import React, { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Container, Card, Form, Button, Alert, Spinner } from "react-bootstrap";
import { Mail, KeyRound, Lock } from "lucide-react";
import authService from "../services/authService";

const extractToken = (resetLink = "") => {
  try {
    const url = new URL(resetLink);
    return url.searchParams.get("token") || "";
  } catch {
    const match = String(resetLink).match(/[?&]token=([^&]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }
};

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [step, setStep] = useState("request"); // request | emailSent | setPassword | done
  const [infoMessage, setInfoMessage] = useState("");
  const [smtpDetail, setSmtpDetail] = useState("");
  const [resetToken, setResetToken] = useState("");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [resetting, setResetting] = useState(false);

  const canSubmitReset = useMemo(
    () => Boolean(resetToken) && password.length >= 6 && password === confirmPassword,
    [resetToken, password, confirmPassword],
  );

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setError("");
    setSmtpDetail("");
    setLoading(true);
    try {
      const response = await authService.forgotPassword(email.trim().toLowerCase());
      const data = response.data || {};
      const token = extractToken(data.resetLink || "");

      if (data.deliveryError) {
        setSmtpDetail(data.deliveryError);
      }

      if (data.emailDelivered) {
        setInfoMessage(
          data.message ||
            "If an account exists with that email, a password reset link has been sent. Check your inbox and spam folder.",
        );
        setStep("emailSent");
        return;
      }

      if (token) {
        setResetToken(token);
        setInfoMessage(
          data.message ||
            "Enter a new password below to finish resetting your account.",
        );
        setStep("setPassword");
        return;
      }

      setInfoMessage(
        data.message ||
          "If an account exists with that email, a password reset link has been sent. Check your inbox and spam folder.",
      );
      setStep("emailSent");
    } catch (err) {
      const status = err.response?.status;
      const apiMessage = err.response?.data?.message;
      setError(
        status === 429
          ? "Too many attempts. Please wait a minute and try again."
          : apiMessage || "Something went wrong. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSetNewPassword = async (e) => {
    e.preventDefault();
    setError("");

    if (!resetToken) {
      setError("Reset session expired. Please request a new link.");
      setStep("request");
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

    setResetting(true);
    try {
      await authService.resetPassword(resetToken, password);
      setStep("done");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "This reset session is invalid or has expired. Please try again.",
      );
      setStep("request");
      setResetToken("");
      setPassword("");
      setConfirmPassword("");
    } finally {
      setResetting(false);
    }
  };

  const handleStartOver = () => {
    setStep("request");
    setError("");
    setInfoMessage("");
    setSmtpDetail("");
    setResetToken("");
    setPassword("");
    setConfirmPassword("");
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
              <h2 className="fw-bold">
                {step === "setPassword" ? "Choose New Password" : "Forgot Password"}
              </h2>
              <p className="text-muted mb-0">
                {step === "setPassword"
                  ? "Create a new password for your TimelySync account"
                  : "Enter your email and we will send a reset link"}
              </p>
            </div>

            {error && (
              <Alert variant="danger" className="py-2 small" style={{ whiteSpace: "pre-wrap" }}>
                {error}
              </Alert>
            )}

            {smtpDetail && step !== "request" && (
              <Alert variant="warning" className="py-2 small" style={{ whiteSpace: "pre-wrap" }}>
                <strong>SMTP detail:</strong> {smtpDetail}
              </Alert>
            )}

            {step === "emailSent" && (
              <>
                <Alert variant="success">{infoMessage}</Alert>
                <div className="text-center">
                  <Button variant="link" className="small" onClick={handleStartOver}>
                    Try another email
                  </Button>
                </div>
              </>
            )}

            {step === "done" && (
              <Alert variant="success">
                Password updated successfully. Redirecting you to sign in...
              </Alert>
            )}

            {step === "request" && (
              <Form onSubmit={handleRequestReset} noValidate>
                <Form.Group className="mb-4" controlId="forgotEmail">
                  <Form.Label>Email Address</Form.Label>
                  <div className="position-relative">
                    <Mail
                      size={18}
                      className="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"
                    />
                    <Form.Control
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="ps-5 py-2"
                      autoComplete="email"
                      required
                      disabled={loading}
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
                      <Spinner size="sm" animation="border" /> Sending email...
                    </>
                  ) : (
                    "Send Reset Email"
                  )}
                </Button>
              </Form>
            )}

            {step === "setPassword" && (
              <>
                {infoMessage && (
                  <Alert variant="info" className="py-2 small">
                    {infoMessage}
                  </Alert>
                )}
                <Form onSubmit={handleSetNewPassword} noValidate>
                  <Form.Group className="mb-3" controlId="newPassword">
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
                        autoComplete="new-password"
                        required
                        disabled={resetting}
                      />
                    </div>
                  </Form.Group>

                  <Form.Group className="mb-4" controlId="confirmNewPassword">
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
                        autoComplete="new-password"
                        required
                        disabled={resetting}
                      />
                    </div>
                  </Form.Group>

                  <Button
                    type="submit"
                    variant="primary"
                    className="w-100 py-2 fw-semibold d-flex align-items-center justify-content-center gap-2"
                    disabled={resetting || !canSubmitReset}
                  >
                    {resetting ? (
                      <>
                        <Spinner size="sm" animation="border" /> Saving...
                      </>
                    ) : (
                      "Save New Password"
                    )}
                  </Button>
                </Form>
                <div className="text-center mt-3">
                  <Button variant="link" className="small" onClick={handleStartOver}>
                    Start over
                  </Button>
                </div>
              </>
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

export default ForgotPassword;
