// src/components/tasks/ImpactSimulationModal.jsx
import React from "react";
import { Modal, Button, ProgressBar, Alert } from "react-bootstrap";
import { AlertTriangle, Briefcase, Award, Calendar } from "lucide-react";

const ImpactSimulationModal = ({ show, onHide, task }) => {
  if (!task?.impactSimulation) return null;

  const { consequences, severityLevel, category } = task.impactSimulation;

  const getSeverityColor = () => {
    switch (severityLevel) {
      case "CRITICAL":
        return "danger";
      case "SERIOUS":
        return "warning";
      default:
        return "info";
    }
  };

  const getCategoryIcon = () => {
    switch (category) {
      case "OPPORTUNITY":
        return <Briefcase size={24} />;
      case "ACADEMIC":
        return <Award size={24} />;
      default:
        return <Calendar size={24} />;
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header
        closeButton
        className={`bg-${getSeverityColor()} text-white`}
      >
        <Modal.Title className="d-flex align-items-center gap-2">
          <AlertTriangle size={20} />
          Impact Simulation
        </Modal.Title>
      </Modal.Header>
      <Modal.Body className="p-4">
        <div className="text-center mb-4">
          <div
            className={`d-inline-flex p-3 rounded-circle bg-${getSeverityColor()} bg-opacity-10 mb-3`}
          >
            {getCategoryIcon()}
          </div>
          <h4>If you miss "{task.title}"</h4>
          <p className="text-muted">Here's what's at stake</p>
        </div>

        <Alert variant={getSeverityColor()} className="mb-4">
          <AlertTriangle size={16} className="me-2" />
          <strong>Severity Level: {severityLevel}</strong>
        </Alert>

        <h6 className="fw-semibold mb-3">Potential Consequences</h6>
        {consequences?.map((consequence, idx) => (
          <div key={idx} className="mb-3">
            <div className="d-flex justify-content-between mb-1">
              <span className="fw-medium">{consequence.description}</span>
              <span
                className={`text-${consequence.probabilityPercent > 70 ? "danger" : "warning"}`}
              >
                {consequence.probabilityPercent}% probability
              </span>
            </div>
            <ProgressBar
              now={consequence.probabilityPercent}
              variant={
                consequence.probabilityPercent > 70 ? "danger" : "warning"
              }
              style={{ height: "8px" }}
            />
          </div>
        ))}

        <div className="bg-light p-3 rounded mt-4">
          <h6 className="fw-semibold mb-2">What you can do now:</h6>
          <ul className="mb-0">
            <li>Break down this task into smaller steps</li>
            <li>Set daily reminders to track progress</li>
            <li>Start at least 3-5 days before deadline</li>
          </ul>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        <Button variant={getSeverityColor()}>Create Recovery Plan</Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ImpactSimulationModal;
