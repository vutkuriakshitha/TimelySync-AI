// src/components/common/LoadingSpinner.jsx
import React from "react";
import { Spinner, Container } from "react-bootstrap";

const LoadingSpinner = ({ message = "Loading..." }) => {
  return (
    <Container className="d-flex justify-content-center align-items-center min-vh-100">
      <div className="text-center">
        <Spinner animation="border" variant="primary" size="lg" />
        <p className="mt-3 text-muted">{message}</p>
      </div>
    </Container>
  );
};

export default LoadingSpinner;