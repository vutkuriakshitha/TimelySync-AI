// src/pages/Events.jsx
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
import { PlusCircle, Search, Calendar, MapPin } from "lucide-react";
import { TaskContext } from "../context/TaskContext";

const Events = () => {
  const navigate = useNavigate();
  const { tasks } = useContext(TaskContext);
  const [searchTerm, setSearchTerm] = useState("");

  const eventTasks = tasks.filter((task) => task.category === "EVENT");

  const filteredTasks = eventTasks.filter((task) =>
    task.title.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const formatDateTime = (date) => {
    return new Date(date).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const isToday = (date) => {
    const today = new Date().toDateString();
    return new Date(date).toDateString() === today;
  };

  return (
    <Container fluid className="py-4">
      <Row className="mb-4 align-items-center">
        <Col>
          <h2 className="text-primary mb-1">Events & Commitments</h2>
          <p className="text-muted">
            College events, meetings, and personal commitments
          </p>
        </Col>
        <Col xs="auto">
          <Button
            variant="primary"
            onClick={() => navigate("/create-task?category=EVENT")}
          >
            <PlusCircle size={18} className="me-2" />
            Add Event
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
              placeholder="Search events..."
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
                className={`shadow-sm h-100 hover-shadow ${isToday(task.dueDate) ? "border-primary" : ""}`}
                onClick={() => navigate(`/task/${task.id}`)}
                style={{ cursor: "pointer" }}
              >
                <Card.Body>
                  {isToday(task.dueDate) && (
                    <Badge bg="primary" className="mb-2">
                      Today
                    </Badge>
                  )}
                  <h5 className="mb-2">{task.title}</h5>

                  <div className="mb-2">
                    <div className="d-flex align-items-center gap-2 mb-1">
                      <Calendar size={14} className="text-muted" />
                      <small>{formatDateTime(task.dueDate)}</small>
                    </div>
                    {task.location && (
                      <div className="d-flex align-items-center gap-2">
                        <MapPin size={14} className="text-muted" />
                        <small className="text-muted">{task.location}</small>
                      </div>
                    )}
                  </div>

                  {task.description && (
                    <p className="text-muted small mb-0">
                      {task.description.substring(0, 80)}...
                    </p>
                  )}
                </Card.Body>
              </Card>
            </Col>
          ))
        ) : (
          <Col>
            <div className="text-center py-5">
              <Calendar size={48} className="text-muted mb-3" />
              <h6 className="text-muted">No events scheduled</h6>
              <Button
                variant="primary"
                onClick={() => navigate("/create-task?category=EVENT")}
                className="mt-2"
              >
                <PlusCircle className="me-2" />
                Add an event
              </Button>
            </div>
          </Col>
        )}
      </Row>
    </Container>
  );
};

export default Events;
