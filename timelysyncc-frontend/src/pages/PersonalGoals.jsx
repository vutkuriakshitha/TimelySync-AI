// src/pages/PersonalGoals.jsx
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
  ProgressBar,
} from "react-bootstrap";
import { PlusCircle, Search, Target, Award } from "lucide-react";
import { TaskContext } from "../context/TaskContext";

const PersonalGoals = () => {
  const navigate = useNavigate();
  const { tasks } = useContext(TaskContext);
  const [searchTerm, setSearchTerm] = useState("");

  const goalTasks = tasks.filter((task) => task.category === "PERSONAL_GOAL");

  const filteredTasks = goalTasks.filter((task) =>
    task.title.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const calculateProgress = (task) => {
    if (task.subtasks?.length) {
      const completed = task.subtasks.filter((s) => s.completed).length;
      return Math.round((completed / task.subtasks.length) * 100);
    }
    return task.status === "COMPLETED" ? 100 : 0;
  };

  return (
    <Container fluid className="py-4">
      <Row className="mb-4 align-items-center">
        <Col>
          <h2 className="text-primary mb-1">Personal Goals</h2>
          <p className="text-muted">
            Track your skills, projects, and milestones
          </p>
        </Col>
        <Col xs="auto">
          <Button
            variant="primary"
            onClick={() => navigate("/create-task?category=PERSONAL_GOAL")}
          >
            <PlusCircle size={18} className="me-2" />
            Add Goal
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
              placeholder="Search goals..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
      </Row>

      <Row>
        {filteredTasks.length > 0 ? (
          filteredTasks.map((task) => {
            const progress = calculateProgress(task);
            return (
              <Col md={6} key={task.id} className="mb-4">
                <Card
                  className="shadow-sm hover-shadow"
                  onClick={() => navigate(`/task/${task.id}`)}
                  style={{ cursor: "pointer" }}
                >
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <div className="d-flex align-items-center gap-2">
                        <Target size={24} className="text-primary" />
                        <h5 className="mb-0">{task.title}</h5>
                      </div>
                      <Badge
                        bg={task.status === "COMPLETED" ? "success" : "primary"}
                        pill
                      >
                        {task.status === "COMPLETED"
                          ? "Achieved"
                          : "In Progress"}
                      </Badge>
                    </div>

                    <div className="mb-3">
                      <div className="d-flex justify-content-between mb-1">
                        <small className="text-muted">Progress</small>
                        <small className="fw-semibold">{progress}%</small>
                      </div>
                      <ProgressBar
                        now={progress}
                        variant={progress === 100 ? "success" : "primary"}
                        style={{ height: "8px" }}
                      />
                    </div>

                    {task.dueDate && (
                      <small className="text-muted">
                        Target: {new Date(task.dueDate).toLocaleDateString()}
                      </small>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            );
          })
        ) : (
          <Col>
            <div className="text-center py-5">
              <Award size={48} className="text-muted mb-3" />
              <h6 className="text-muted">No personal goals set</h6>
              <Button
                variant="primary"
                onClick={() => navigate("/create-task?category=PERSONAL_GOAL")}
                className="mt-2"
              >
                <PlusCircle className="me-2" />
                Set your first goal
              </Button>
            </div>
          </Col>
        )}
      </Row>
    </Container>
  );
};

export default PersonalGoals;
