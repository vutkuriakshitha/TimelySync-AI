// src/components/common/ErrorBoundary.jsx
import React from "react";
import { Container, Button } from "react-bootstrap";
import { AlertTriangle } from "lucide-react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Centralized place to send this to an error-tracking service in production.
    console.error("Unhandled UI error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false });
    window.location.href = "/dashboard";
  };

  render() {
    if (this.state.hasError) {
      return (
        <Container className="d-flex flex-column align-items-center justify-content-center min-vh-100 text-center">
          <AlertTriangle size={56} className="text-danger mb-3" />
          <h3>Something went wrong</h3>
          <p className="text-muted mb-4">
            An unexpected error occurred. You can try returning to the dashboard.
          </p>
          <Button variant="primary" onClick={this.handleReset}>
            Back to Dashboard
          </Button>
        </Container>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
