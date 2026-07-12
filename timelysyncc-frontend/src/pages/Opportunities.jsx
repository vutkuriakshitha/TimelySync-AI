// src/pages/Opportunities.jsx
import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  Form,
  InputGroup,
} from "react-bootstrap";
import {
  PlusCircle,
  Search,
  Calendar,
  Briefcase,
  Award,
} from "lucide-react";
import { TaskContext } from "../context/TaskContext";

const Opportunities = () => {
  const navigate = useNavigate();
  const { tasks } = useContext(TaskContext);
  const [searchTerm, setSearchTerm] = useState("");

  const opportunityTasks = tasks.filter(
    (task) => task.category === "OPPORTUNITY",
  );

  const filteredTasks = opportunityTasks.filter(
    (task) =>
      task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (task.description &&
        task.description.toLowerCase().includes(searchTerm.toLowerCase())),
  );

  const getRiskBadge = (riskLevel, riskScore) => {
    if (riskLevel === "CRITICAL") {
      return (
        <Badge bg="danger" pill>
          Critical ({riskScore}%)
        </Badge>
      );
    }
    if (riskLevel === "WARNING") {
      return (
        <Badge bg="warning" pill>
          Warning ({riskScore}%)
        </Badge>
      );
    }
    return (
      <Badge bg="success" pill>
        Safe ({riskScore}%)
      </Badge>
    );
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <Container fluid className="py-4">
      <Row className="mb-4 align-items-center">
        <Col>
          <h2 className="text-primary mb-1">Opportunities</h2>
          <p className="text-muted">
            Scholarships, internships, workshops, and more
          </p>
        </Col>
        <Col xs="auto">
          <Button
            variant="primary"
            onClick={() => navigate("/create-task?category=OPPORTUNITY")}
          >
            <PlusCircle size={18} className="me-2" />
            Add Opportunity
          </Button>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text className="bg-white">
              <Search size={18} />
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search opportunities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
      </Row>

      <Row>
        {filteredTasks.length > 0 ? (
          filteredTasks.map((task) => (
            <Col md={6} lg={4} key={task.id} className="mb-4">
              <Card
                className="shadow-sm h-100 hover-shadow"
                onClick={() => navigate(`/task/${task.id}`)}
                style={{ cursor: "pointer" }}
              >
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <Briefcase size={24} className="text-primary mb-2" />
                      <h5 className="mb-0">{task.title}</h5>
                    </div>
                    {task.riskAnalysis &&
                      getRiskBadge(task.riskAnalysis.riskLevel, task.riskAnalysis.riskScore)}
                  </div>

                  {task.description && (
                    <p className="text-muted small mb-3">
                      {task.description.substring(0, 100)}...
                    </p>
                  )}

                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <small className="text-muted d-flex align-items-center gap-1">
                        <Calendar size={12} /> Due: {formatDate(task.dueDate)}
                      </small>
                    </div>
                    {task.impact && (
                      <Badge
                        bg={
                          task.impact === "HIGH"
                            ? "danger"
                            : task.impact === "MEDIUM"
                              ? "warning"
                              : "info"
                        }
                        pill
                      >
                        {task.impact} Impact
                      </Badge>
                    )}
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))
        ) : (
          <Col>
            <div className="text-center py-5">
              <Award size={48} className="text-muted mb-3" />
              <h6 className="text-muted">No opportunities found</h6>
              <Button
                variant="primary"
                onClick={() => navigate("/create-task?category=OPPORTUNITY")}
                className="mt-2"
              >
                <PlusCircle className="me-2" />
                Add your first opportunity
              </Button>
            </div>
          </Col>
        )}
      </Row>
    </Container>
  );
};

export default Opportunities;
