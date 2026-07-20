// src/pages/Login.jsx
import React, { useState, useContext } from "react";
import { Link } from "react-router-dom";
import { Container, Card, Form, Button, Alert, Spinner } from "react-bootstrap";
import { LogIn, Mail, Lock } from "lucide-react";
import { AuthContext } from "../context/AuthContext";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await login(email.trim().toLowerCase(), password);
      if (!result.success) {
        setError(result.error);
      }
    } catch (err) {
      setError("Could not reach the server. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-gradient-primary">
      <Container className="d-flex justify-content-center">
        <Card
          className="shadow-lg border-0"
          style={{ width: "100%", maxWidth: "450px" }}
        >
          <Card.Body className="p-5">
            <div className="text-center mb-4">
              <div className="bg-primary text-white rounded-circle d-inline-flex p-3 mb-3">
                <LogIn size={32} />
              </div>
              <h2 className="fw-bold">Sign In</h2>
              <p className="text-muted">Welcome back to TimelySync</p>
            </div>

            {error && (
              <Alert variant="danger" className="py-2 small">
                {error}
              </Alert>
            )}

            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3" controlId="email">
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

              <Form.Group className="mb-4" controlId="password">
                <div className="d-flex justify-content-between align-items-center">
                  <Form.Label>Password</Form.Label>
                  <Link
                    to="/forgot-password"
                    className="small text-primary text-decoration-none"
                  >
                    Forgot password?
                  </Link>
                </div>
                <div className="position-relative">
                  <Lock
                    size={18}
                    className="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"
                  />
                  <Form.Control
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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
                    <Spinner size="sm" animation="border" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>
            </Form>

            <div className="text-center mt-4">
              <p className="text-muted small">
                Don't have an account?{" "}
                <Link
                  to="/signup"
                  className="text-primary fw-bold text-decoration-none"
                >
                  Create one now
                </Link>
              </p>
            </div>
          </Card.Body>
        </Card>
      </Container>
    </div>
  );
};

export default Login;
