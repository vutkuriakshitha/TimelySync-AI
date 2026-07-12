// src/components/dashboard/QuickActions.jsx
import React from "react";
import { Card, Button, ListGroup } from "react-bootstrap";
import { Plus, Brain, Calendar, FileText, Settings, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

const QuickActions = ({ onClose }) => {
  const navigate = useNavigate();

  const actions = [
    {
      icon: Plus,
      label: "Quick Task",
      description: "Add a task quickly",
      color: "primary",
      onClick: () => navigate("/create-task"),
    },
    {
      icon: Brain,
      label: "Smart Intake",
      description: "AI-powered task creation",
      color: "info",
      onClick: () => navigate("/create-task?smart=true"),
    },
    {
      icon: Calendar,
      label: "Today's Snapshot",
      description: "See your schedule",
      color: "success",
      onClick: () => navigate("/today"),
    },
    {
      icon: FileText,
      label: "Accountability",
      description: "Track your progress",
      color: "warning",
      onClick: () => navigate("/accountability"),
    },
    {
      icon: Settings,
      label: "Settings",
      description: "Customize experience",
      color: "secondary",
      onClick: () => navigate("/settings"),
    },
  ];

  return (
    <Card className="h-100 border-0 shadow-sm">
      <Card.Header className="d-flex justify-content-between align-items-center bg-white">
        <h5 className="mb-0 fw-semibold">Quick Actions</h5>
        <Button variant="link" className="p-0 text-secondary" onClick={onClose}>
          <X size={18} />
        </Button>
      </Card.Header>
      <Card.Body className="p-0">
        <ListGroup variant="flush">
          {actions.map((action, index) => (
            <ListGroup.Item
              key={index}
              action
              onClick={action.onClick}
              className="py-3 cursor-pointer"
            >
              <div className="d-flex align-items-center gap-3">
                <div
                  className={`bg-${action.color} bg-opacity-10 p-2 rounded-circle`}
                >
                  <action.icon size={20} className={`text-${action.color}`} />
                </div>
                <div className="flex-grow-1">
                  <h6 className="mb-0">{action.label}</h6>
                  <small className="text-muted">{action.description}</small>
                </div>
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Card.Body>
    </Card>
  );
};

export default QuickActions;
