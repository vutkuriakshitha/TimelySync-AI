// src/pages/TodaySnapshot.jsx
import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  ListGroup,
} from "react-bootstrap";
import {
  Calendar,
  Clock,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
} from "lucide-react";
import { TaskContext } from "../context/TaskContext";

const TodaySnapshot = () => {
  const navigate = useNavigate();
  const { tasks, completeTask } = useContext(TaskContext);
  const [todayTasks, setTodayTasks] = useState([]);
  const [overdueTasks, setOverdueTasks] = useState([]);

  useEffect(() => {
    const today = new Date().toDateString();
    const todayFiltered = tasks.filter((task) => {
      if (task.status === "COMPLETED") return false;
      return task.dueDate && new Date(task.dueDate).toDateString() === today;
    });

    const overdue = tasks.filter((task) => {
      if (task.status === "COMPLETED") return false;
      return task.dueDate && new Date(task.dueDate) < new Date();
    });

    setTodayTasks(todayFiltered);
    setOverdueTasks(overdue);
  }, [tasks]);

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <h2 className="text-primary mb-1">Today's Snapshot</h2>
          <p className="text-muted">
            {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        </Col>
      </Row>

      {/* Stats Cards */}
      <Row className="mb-4 g-3">
        <Col md={4}>
          <Card className="shadow-sm border-0 bg-primary text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6>Due Today</h6>
                  <h2 className="mb-0">{todayTasks.length}</h2>
                </div>
                <Calendar size={32} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm border-0 bg-danger text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6>Overdue</h6>
                  <h2 className="mb-0">{overdueTasks.length}</h2>
                </div>
                <AlertTriangle size={32} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm border-0 bg-success text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6>Completed Today</h6>
                  <h2 className="mb-0">
                    {
                      tasks.filter(
                        (t) =>
                          t.status === "COMPLETED" &&
                          t.completedAt &&
                          new Date(t.completedAt).toDateString() ===
                            new Date().toDateString(),
                      ).length
                    }
                  </h2>
                </div>
                <CheckCircle size={32} />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Today's Tasks */}
      <Row>
        <Col lg={6} className="mb-4">
          <Card className="shadow-sm h-100">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0">Due Today</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {todayTasks.length > 0 ? (
                <ListGroup variant="flush">
                  {todayTasks.map((task) => (
                    <ListGroup.Item
                      key={task.id}
                      className="d-flex justify-content-between align-items-center py-3"
                    >
                      <div>
                        <h6 className="mb-1">{task.title}</h6>
                        <small className="text-muted d-flex align-items-center gap-1">
                          <Clock size={12} /> {formatTime(task.dueDate)}
                        </small>
                      </div>
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => completeTask(task.id)}
                      >
                        <CheckCircle size={14} className="me-1" />
                        Complete
                      </Button>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              ) : (
                <div className="text-center py-5">
                  <CheckCircle size={48} className="text-success mb-3" />
                  <p className="text-muted">No tasks due today!</p>
                  <p className="small text-muted">Enjoy your day 🎉</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Overdue Tasks */}
        <Col lg={6} className="mb-4">
          <Card className="shadow-sm h-100">
            <Card.Header className="bg-danger text-white">
              <h5 className="mb-0">Overdue Tasks</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {overdueTasks.length > 0 ? (
                <ListGroup variant="flush">
                  {overdueTasks.map((task) => (
                    <ListGroup.Item key={task.id} className="py-3">
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 className="mb-1">{task.title}</h6>
                          <small className="text-danger">
                            Due: {new Date(task.dueDate).toLocaleDateString()}
                          </small>
                        </div>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => navigate(`/task/${task.id}`)}
                        >
                          View <ArrowRight size={12} />
                        </Button>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              ) : (
                <div className="text-center py-5">
                  <CheckCircle size={48} className="text-success mb-3" />
                  <p className="text-muted">No overdue tasks!</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Upcoming This Week */}
      <Row>
        <Col>
          <Card className="shadow-sm">
            <Card.Header className="bg-info text-white">
              <h5 className="mb-0">This Week's Schedule</h5>
            </Card.Header>
            <Card.Body>
              {tasks
                .filter((t) => {
                  if (t.status === "COMPLETED") return false;
                  const dueDate = new Date(t.dueDate);
                  const weekEnd = new Date();
                  weekEnd.setDate(weekEnd.getDate() + 7);
                  return dueDate > new Date() && dueDate <= weekEnd;
                })
                .slice(0, 5)
                .map((task) => (
                  <div
                    key={task.id}
                    className="d-flex justify-content-between align-items-center py-2 border-bottom"
                  >
                    <div>
                      <span className="fw-semibold">{task.title}</span>
                      <small className="text-muted d-block">
                        {new Date(task.dueDate).toLocaleDateString("en-US", {
                          weekday: "short",
                          month: "short",
                          day: "numeric",
                        })}
                      </small>
                    </div>
                    <Badge bg="info" pill>
                      {task.category?.replace("_", " ")}
                    </Badge>
                  </div>
                ))}
              {tasks.filter(
                (t) =>
                  t.status !== "COMPLETED" &&
                  new Date(t.dueDate) > new Date() &&
                  new Date(t.dueDate) <=
                    new Date(new Date().setDate(new Date().getDate() + 7)),
              ).length === 0 && (
                <p className="text-center text-muted py-3">
                  No upcoming tasks this week
                </p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default TodaySnapshot;
