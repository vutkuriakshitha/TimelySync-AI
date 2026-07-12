// src/pages/ForgotPassword.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Container, Card, Form, Button, Alert, Spinner } from "react-bootstrap";
import { Mail, KeyRound } from "lucide-react";
import authService from "../services/authService";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authService.forgotPassword(email);
      setSubmitted(true);
    } catch (err) {
      setError(
        err.response?.data?.message || "Something went wrong. Please try again.",
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
              <h2 className="fw-bold">Forgot Password</h2>
              <p className="text-muted">
                Enter your email and we'll send you a reset link
              </p>
            </div>

            {error && (
              <Alert variant="danger" className="py-2 small">
                {error}
              </Alert>
            )}

            {submitted ? (
              <Alert variant="success">
                If an account exists with that email, a password reset link has
                been sent. Please check your inbox.
              </Alert>
            ) : (
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-4" controlId="email">
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
                      <Spinner size="sm" animation="border" /> Sending...
                    </>
                  ) : (
                    "Send Reset Link"
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

export default ForgotPassword;
