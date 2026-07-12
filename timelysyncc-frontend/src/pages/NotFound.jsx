// src/pages/NotFound.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { Container, Row, Col, Button } from "react-bootstrap";
import { Home } from "lucide-react";

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100">
      <Row className="text-center">
        <Col>
          <div className="display-1 text-primary fw-bold mb-4">404</div>
          <h1 className="mb-3">Page Not Found</h1>
          <p className="text-muted mb-4">
            Oops! The page you're looking for doesn't exist or has been moved.
          </p>
          <div className="d-flex gap-3 justify-content-center">
            <Button variant="primary" onClick={() => navigate("/dashboard")}>
              <Home size={18} className="me-2" />
              Go to Dashboard
            </Button>
            <Button variant="outline-primary" onClick={() => navigate(-1)}>
              Go Back
            </Button>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default NotFound;
