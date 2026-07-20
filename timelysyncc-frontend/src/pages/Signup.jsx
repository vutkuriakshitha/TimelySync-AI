// src/pages/Signup.jsx
import React, { useState, useContext } from "react";
import { Link } from "react-router-dom";
import { Container, Card, Form, Button, Alert, Spinner } from "react-bootstrap";
import { UserPlus, User, Mail, Lock } from "lucide-react";
import { AuthContext } from "../context/AuthContext";

const Signup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setError("");

    const trimmedName = name.trim();
    const trimmedEmail = email.trim().toLowerCase();

    if (!trimmedName) {
      setError("Please enter your full name");
      return;
    }
    if (!trimmedEmail) {
      setError("Please enter your email");
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
      const result = await register(trimmedName, trimmedEmail, password);
      if (!result?.success) {
        setError(result?.error || "Registration failed. Please try again.");
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
          style={{ width: "100%", maxWidth: "500px" }}
        >
          <Card.Body className="p-5">
            <div className="text-center mb-4">
              <div className="bg-success text-white rounded-circle d-inline-flex p-3 mb-3">
                <UserPlus size={32} />
              </div>
              <h2 className="fw-bold">Create Account</h2>
              <p className="text-muted">
                Join TimelySync and never miss a deadline
              </p>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            <Form onSubmit={handleSubmit} noValidate>
              <Form.Group className="mb-3" controlId="signupName">
                <Form.Label>Full Name</Form.Label>
                <div className="position-relative">
                  <User
                    size={18}
                    className="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"
                  />
                  <Form.Control
                    type="text"
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="ps-5 py-2"
                    autoComplete="name"
                    required
                    disabled={loading}
                  />
                </div>
              </Form.Group>

              <Form.Group className="mb-3" controlId="signupEmail">
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

              <Form.Group className="mb-3" controlId="signupPassword">
                <Form.Label>Password</Form.Label>
                <div className="position-relative">
                  <Lock
                    size={18}
                    className="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"
                  />
                  <Form.Control
                    type="password"
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="ps-5 py-2"
                    autoComplete="new-password"
                    required
                    disabled={loading}
                  />
                </div>
              </Form.Group>

              <Form.Group className="mb-4" controlId="signupConfirmPassword">
                <Form.Label>Confirm Password</Form.Label>
                <div className="position-relative">
                  <Lock
                    size={18}
                    className="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"
                  />
                  <Form.Control
                    type="password"
                    placeholder="Confirm your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="ps-5 py-2"
                    autoComplete="new-password"
                    required
                    disabled={loading}
                  />
                </div>
              </Form.Group>

              <Button
                type="submit"
                variant="success"
                className="w-100 py-2 fw-semibold d-flex align-items-center justify-content-center gap-2"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Spinner size="sm" animation="border" /> Creating Account...
                  </>
                ) : (
                  "Create Account"
                )}
              </Button>
            </Form>

            <div className="text-center mt-4">
              <p className="text-muted mb-0">
                Already have an account?{" "}
                <Link to="/login" className="text-success text-decoration-none fw-semibold">
                  Sign in
                </Link>
              </p>
            </div>
          </Card.Body>
        </Card>
      </Container>
    </div>
  );
};

export default Signup;
