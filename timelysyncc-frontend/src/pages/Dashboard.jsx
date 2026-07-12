// src/pages/Dashboard.jsx
import React, {
  useState,
  useEffect,
  useContext,
  useCallback,
  useMemo,
} from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  ProgressBar,
  ListGroup,
  Spinner,
  Form,
  InputGroup,
  Dropdown,
  Modal,
} from "react-bootstrap";
import {
  Plus,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  Search,
  X,
  Shield,
  BarChart3,
  Eye,
  Sparkles,
  AlertOctagon,
  Award,
  Star,
  Gift,
  Activity,
} from "lucide-react";
import { TaskContext } from "../context/TaskContext";
import { AuthContext } from "../context/AuthContext";
import dashboardService from "../services/dashboardService";
import statsService from "../services/statsService";
import ImpactSimulationModal from "../components/tasks/ImpactSimulationModal";
import CognitiveLoadWarning from "../components/dashboard/CognitiveLoadWarning";
import FailurePredictionCard from "../components/tasks/FailurePredictionCard";

const DASHBOARD_POLL_MS = Number(process.env.REACT_APP_DASHBOARD_POLL_MS) || 60000;

const Dashboard = () => {
  const navigate = useNavigate();
  const {
    tasks,
    stats,
    loading,
    getTodayTasks,
    getHighRiskTasks,
    getUpcomingTasks,
    getOverdueTasks,
    completeTask,
    failurePredictions,
  } = useContext(TaskContext);

  const { user } = useContext(AuthContext);

  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("ALL");
  const [sortBy, setSortBy] = useState("dueDate");
  const [sortOrder, setSortOrder] = useState("asc");
  const [selectedTask, setSelectedTask] = useState(null);
  const [showImpactModal, setShowImpactModal] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [taskToComplete, setTaskToComplete] = useState(null);
  const [completionProof, setCompletionProof] = useState(null);
  const [dashboardAnalytics, setDashboardAnalytics] = useState(null);
  const [userStats, setUserStats] = useState({
    streak: 0,
    achievements: [],
    level: 1,
    xp: 0,
    nextLevelXp: 1000,
    coins: 0,
  });
  const [showAchievementModal, setShowAchievementModal] = useState(false);
  const [newAchievement, setNewAchievement] = useState(null);

  const loadUserStats = useCallback(async () => {
    try {
      const response = await statsService.getStats();
      setUserStats(response.data);
    } catch (error) {
      console.error("Error loading user stats:", error);
    }
  }, []);

  const loadDashboardData = useCallback(async () => {
    try {
      const response = await dashboardService.getSummary();
      setDashboardAnalytics(response.data);
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    }
  }, []);

  useEffect(() => {
    loadUserStats();
    loadDashboardData();
    const interval = setInterval(() => {
      loadUserStats();
      loadDashboardData();
    }, DASHBOARD_POLL_MS);
    return () => clearInterval(interval);
  }, [loadUserStats, loadDashboardData, user]);

  const todayTasks = getTodayTasks();
  const highRiskTasks = getHighRiskTasks();
  const upcomingTasks = getUpcomingTasks(7);
  const overdueTasks = getOverdueTasks();

  const getTasksByFilter = useCallback(() => {
    let tasksToFilter = [];

    switch (filterType) {
      case "TODAY":
        tasksToFilter = [...todayTasks];
        break;
      case "UPCOMING":
        tasksToFilter = [...upcomingTasks];
        break;
      case "OVERDUE":
        tasksToFilter = [...overdueTasks];
        break;
      case "HIGH_RISK":
        tasksToFilter = [...highRiskTasks];
        break;
      case "COMPLETED":
        tasksToFilter = tasks.filter((t) => t.status === "COMPLETED");
        break;
      default:
        tasksToFilter = tasks.filter((t) => t.status === "ACTIVE");
        break;
    }

    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      tasksToFilter = tasksToFilter.filter(
        (task) =>
          task.title.toLowerCase().includes(term) ||
          (task.description && task.description.toLowerCase().includes(term)) ||
          (task.tags && task.tags.some((tag) => tag.toLowerCase().includes(term))),
      );
    }

    tasksToFilter = [...tasksToFilter].sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case "dueDate":
          comparison = new Date(a.dueDate) - new Date(b.dueDate);
          break;
        case "riskScore": {
          const riskA = a.riskAnalysis?.riskScore || 0;
          const riskB = b.riskAnalysis?.riskScore || 0;
          comparison = riskA - riskB;
          break;
        }
        case "priority": {
          const priorityWeight = { HIGH: 3, MEDIUM: 2, LOW: 1 };
          comparison =
            (priorityWeight[a.priority] || 0) - (priorityWeight[b.priority] || 0);
          break;
        }
        default:
          comparison = 0;
      }
      return sortOrder === "asc" ? comparison : -comparison;
    });

    return tasksToFilter;
  }, [
    filterType,
    todayTasks,
    upcomingTasks,
    overdueTasks,
    highRiskTasks,
    tasks,
    searchTerm,
    sortBy,
    sortOrder,
  ]);

  const filteredTasks = getTasksByFilter();

  const getFilterCount = (type) => {
    switch (type) {
      case "ALL":
        return tasks.filter((t) => t.status === "ACTIVE").length;
      case "TODAY":
        return todayTasks.length;
      case "UPCOMING":
        return upcomingTasks.length;
      case "OVERDUE":
        return overdueTasks.length;
      case "HIGH_RISK":
        return highRiskTasks.length;
      case "COMPLETED":
        return tasks.filter((t) => t.status === "COMPLETED").length;
      default:
        return 0;
    }
  };

  const completionRate =
    tasks.length > 0 ? Math.round((stats.completed / tasks.length) * 100) : 0;

  const onTimeRate = useMemo(() => {
    const completedTasks = tasks.filter((t) => t.status === "COMPLETED");
    if (completedTasks.length === 0) return 0;
    const onTime = completedTasks.filter((t) => t.postAnalysis?.completedOnTime);
    return Math.round((onTime.length / completedTasks.length) * 100);
  }, [tasks]);

  const avgRiskScore = useMemo(() => {
    const activeTasks = tasks.filter((t) => t.status === "ACTIVE");
    if (activeTasks.length === 0) return 0;
    const totalRisk = activeTasks.reduce(
      (sum, t) => sum + (t.riskAnalysis?.riskScore || 0),
      0,
    );
    return Math.round(totalRisk / activeTasks.length);
  }, [tasks]);

  const handleCompleteTask = async () => {
    if (!taskToComplete) return;
    try {
      const previousAchievementCount = userStats.achievements?.length || 0;
      await completeTask(taskToComplete.id, completionProof);
      setShowCompleteModal(false);
      setTaskToComplete(null);
      setCompletionProof(null);

      const response = await statsService.getStats();
      setUserStats(response.data);
      const newAchievements = response.data.achievements || [];
      if (newAchievements.length > previousAchievementCount) {
        // Achievements are ordered by unlockedAt descending, so the most
        // recently unlocked one is first.
        setNewAchievement(newAchievements[0]);
        setShowAchievementModal(true);
      }
      loadDashboardData();
    } catch (error) {
      console.error("Error completing task:", error);
    }
  };

  const handleViewImpact = (task) => {
    setSelectedTask(task);
    setShowImpactModal(true);
  };

  const getRiskBadge = (riskLevel, riskScore) => {
    const config = {
      CRITICAL: { bg: "danger", icon: AlertTriangle, text: "Critical" },
      WARNING: { bg: "warning", icon: AlertTriangle, text: "Warning" },
      SAFE: { bg: "success", icon: Shield, text: "Safe" },
    };
    const { bg, icon: Icon, text } = config[riskLevel] || config.SAFE;
    return (
      <Badge bg={bg} pill className="d-flex align-items-center gap-1 px-2 py-1">
        <Icon size={12} />
        <span>{text}</span>
        {riskScore !== undefined && riskScore !== null && (
          <span className="ms-1">({riskScore}%)</span>
        )}
      </Badge>
    );
  };

  const getPriorityBadge = (priority) => {
    const config = {
      HIGH: { bg: "danger", text: "High Priority" },
      MEDIUM: { bg: "warning", text: "Medium Priority" },
      LOW: { bg: "success", text: "Low Priority" },
    };
    const { bg, text } = config[priority] || config.LOW;
    return (
      <Badge bg={bg} pill className="px-2 py-1">
        {text}
      </Badge>
    );
  };

  const getCategoryIcon = (category) => {
    const icons = {
      ACADEMIC: "📚",
      OPPORTUNITY: "💼",
      PERSONAL_GOAL: "🎯",
      EVENT: "📅",
    };
    return icons[category] || "📌";
  };

  const formatDate = (date) => {
    if (!date) return "No due date";
    return new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getDaysRemaining = (dueDate) => {
    if (!dueDate) return "";
    const days = Math.ceil((new Date(dueDate) - new Date()) / (1000 * 60 * 60 * 24));
    if (days < 0) return `${Math.abs(days)} days overdue`;
    if (days === 0) return "Due today";
    return `${days} days left`;
  };

  if (loading) {
    return (
      <Container className="text-center py-5">
        <div>
          <Spinner animation="border" variant="primary" size="lg" />
          <p className="mt-3 text-muted">Loading your dashboard...</p>
        </div>
      </Container>
    );
  }

  const cognitiveLoad = dashboardAnalytics?.cognitiveLoad;

  return (
    <>
      <Container fluid className="py-4 px-4">
        {/* Header */}
        <Row className="mb-4 align-items-center">
          <Col md={8}>
            <div>
              <h2 className="text-primary mb-1 fw-bold">
                Welcome back, {user?.name || "User"}! 👋
              </h2>
              <p className="text-muted mb-0">
                {new Date().toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
          </Col>
          <Col md={4}>
            <div className="d-flex gap-2 justify-content-end">
              <Button variant="outline-primary" onClick={() => navigate("/create-task")}>
                <Plus size={18} className="me-2" />
                Manual Add
              </Button>
              <Button variant="primary" onClick={() => navigate("/create-task?smart=true")}>
                <Sparkles size={18} className="me-2" />
                Smart Intake
              </Button>
            </div>
          </Col>
        </Row>

        {/* User Stats Bar */}
        <Row className="mb-4">
          <Col>
            <Card className="shadow-sm border-0 bg-gradient-primary text-white">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
                  <div className="d-flex align-items-center gap-3">
                    <div className="bg-white bg-opacity-25 p-3 rounded-circle">
                      <Activity size={24} className="text-white" />
                    </div>
                    <div>
                      <small className="text-white-50">Level {userStats.level}</small>
                      <h5 className="text-white mb-0">
                        {userStats.xp} / {userStats.nextLevelXp} XP
                      </h5>
                      <ProgressBar
                        now={(userStats.xp / (userStats.nextLevelXp || 1)) * 100}
                        variant="light"
                        className="mt-1"
                        style={{ height: "4px", width: "200px" }}
                      />
                    </div>
                  </div>
                  <div className="d-flex align-items-center gap-3">
                    <div className="text-center">
                      <Award size={20} className="text-white mb-1" />
                      <div className="text-white">
                        <strong>{userStats.achievements?.length || 0}</strong>
                        <small className="d-block text-white-50">Achievements</small>
                      </div>
                    </div>
                    <div className="text-center">
                      <Star size={20} className="text-warning mb-1" />
                      <div className="text-white">
                        <strong>{userStats.streak}</strong>
                        <small className="d-block text-white-50">Day Streak</small>
                      </div>
                    </div>
                    <div className="text-center">
                      <Gift size={20} className="text-white mb-1" />
                      <div className="text-white">
                        <strong>{userStats.coins}</strong>
                        <small className="d-block text-white-50">Coins</small>
                      </div>
                    </div>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Cognitive Load Warning */}
        {cognitiveLoad?.level === "HIGH" && (
          <Row className="mb-4">
            <Col>
              <CognitiveLoadWarning
                activeCount={cognitiveLoad.activeCount}
                warningMessage={`You have ${cognitiveLoad.highPriorityCount} high-priority tasks among ${cognitiveLoad.activeCount} active tasks. Consider rescheduling or delegating some.`}
                maxCapacity={10}
              />
            </Col>
          </Row>
        )}

        {/* Stats Cards */}
        <Row className="mb-4 g-3">
          <Col md={3}>
            <Card className="shadow-sm border-0 h-100 bg-primary text-white">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <p className="text-white-50 mb-1">Total Tasks</p>
                    <h2 className="text-white mb-0 fw-bold">{tasks.length}</h2>
                    <small className="text-white-50">
                      {stats.active} active · {stats.completed} completed
                    </small>
                  </div>
                  <div className="bg-white-20 p-3 rounded-circle">
                    <Calendar size={28} className="text-white" />
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="shadow-sm border-0 h-100 bg-success text-white">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <p className="text-white-50 mb-1">Completion Rate</p>
                    <h2 className="text-white mb-0 fw-bold">{completionRate}%</h2>
                    <small className="text-white-50">
                      {stats.completed} / {tasks.length} tasks
                    </small>
                  </div>
                  <div className="bg-white-20 p-3 rounded-circle">
                    <CheckCircle size={28} className="text-white" />
                  </div>
                </div>
                <ProgressBar
                  now={completionRate}
                  variant="light"
                  className="mt-3"
                  style={{ height: "6px" }}
                />
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="shadow-sm border-0 h-100 bg-warning text-white">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <p className="text-white-50 mb-1">On-Time Rate</p>
                    <h2 className="text-white mb-0 fw-bold">{onTimeRate}%</h2>
                    <small className="text-white-50">Completed before deadline</small>
                  </div>
                  <div className="bg-white-20 p-3 rounded-circle">
                    <Clock size={28} className="text-white" />
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="shadow-sm border-0 h-100 bg-info text-white">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <p className="text-white-50 mb-1">Avg Risk Score</p>
                    <h2 className="text-white mb-0 fw-bold">{avgRiskScore}%</h2>
                    <small className="text-white-50">{highRiskTasks.length} high risk tasks</small>
                  </div>
                  <div className="bg-white-20 p-3 rounded-circle">
                    <Shield size={28} className="text-white" />
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Search and Filters */}
        <Row className="mb-4">
          <Col md={5}>
            <InputGroup>
              <InputGroup.Text className="bg-white border-end-0">
                <Search size={18} className="text-muted" />
              </InputGroup.Text>
              <Form.Control
                type="text"
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="border-start-0"
              />
              {searchTerm && (
                <Button variant="outline-secondary" onClick={() => setSearchTerm("")}>
                  <X size={18} />
                </Button>
              )}
            </InputGroup>
          </Col>
          <Col md={4}>
            <Dropdown>
              <Dropdown.Toggle variant="outline-secondary" size="sm">
                <BarChart3 size={14} className="me-1" />
                Sort:{" "}
                {sortBy === "dueDate" ? "Due Date" : sortBy === "riskScore" ? "Risk" : "Priority"}
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <Dropdown.Item onClick={() => setSortBy("dueDate")}>Due Date</Dropdown.Item>
                <Dropdown.Item onClick={() => setSortBy("riskScore")}>Risk Score</Dropdown.Item>
                <Dropdown.Item onClick={() => setSortBy("priority")}>Priority</Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}>
                  Toggle Order ({sortOrder === "asc" ? "Ascending" : "Descending"})
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </Col>
          <Col md={3}>
            <div className="d-flex gap-2 justify-content-end flex-wrap">
              {["ALL", "TODAY", "UPCOMING", "OVERDUE", "HIGH_RISK", "COMPLETED"].map((type) => (
                <Button
                  key={type}
                  variant={filterType === type ? "primary" : "outline-primary"}
                  size="sm"
                  onClick={() => setFilterType(type)}
                >
                  {type === "ALL" && "All Active"}
                  {type === "TODAY" && `Today (${getFilterCount("TODAY")})`}
                  {type === "UPCOMING" && `Upcoming (${getFilterCount("UPCOMING")})`}
                  {type === "OVERDUE" && `Overdue (${getFilterCount("OVERDUE")})`}
                  {type === "HIGH_RISK" && `High Risk (${getFilterCount("HIGH_RISK")})`}
                  {type === "COMPLETED" && `Completed (${getFilterCount("COMPLETED")})`}
                </Button>
              ))}
            </div>
          </Col>
        </Row>

        {/* Main Content */}
        <Row>
          <Col lg={4}>
            <FailurePredictionCard predictions={failurePredictions} />

            {highRiskTasks.length > 0 && (
              <Card className="shadow-sm mb-4 border-danger">
                <Card.Header className="bg-danger text-white">
                  <div className="d-flex align-items-center gap-2">
                    <AlertOctagon size={18} />
                    <h6 className="mb-0 fw-semibold">Critical Alerts</h6>
                    <Badge bg="light" text="danger" pill className="ms-auto">
                      {highRiskTasks.length}
                    </Badge>
                  </div>
                </Card.Header>
                <ListGroup variant="flush">
                  {highRiskTasks.slice(0, 3).map((task) => (
                    <ListGroup.Item
                      key={task.id}
                      action
                      onClick={() => navigate(`/task/${task.id}`)}
                      className="py-3"
                    >
                      <div className="d-flex justify-content-between">
                        <div>
                          <div className="d-flex align-items-center gap-2 mb-1">
                            <span>{getCategoryIcon(task.category)}</span>
                            <span className="fw-semibold">{task.title}</span>
                          </div>
                          <div className="d-flex gap-3 small text-muted">
                            <span>Due: {formatDate(task.dueDate)}</span>
                            <span className="text-danger">{getDaysRemaining(task.dueDate)}</span>
                          </div>
                        </div>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewImpact(task);
                          }}
                        >
                          Impact
                        </Button>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card>
            )}
          </Col>

          <Col lg={8}>
            <Card className="shadow-sm">
              <Card.Header className="bg-white d-flex justify-content-between align-items-center py-3">
                <div>
                  <h5 className="mb-0 fw-semibold">
                    {filterType === "ALL" && "Active Tasks"}
                    {filterType === "TODAY" && "Today's Tasks"}
                    {filterType === "UPCOMING" && "Upcoming Tasks"}
                    {filterType === "OVERDUE" && "Overdue Tasks"}
                    {filterType === "HIGH_RISK" && "High Risk Tasks"}
                    {filterType === "COMPLETED" && "Completed Tasks"}
                  </h5>
                  <small className="text-muted">{filteredTasks.length} tasks found</small>
                </div>
                <Badge bg="primary" pill>
                  {filteredTasks.length}
                </Badge>
              </Card.Header>
              <Card.Body className="p-0">
                {filteredTasks.length > 0 ? (
                  <ListGroup variant="flush">
                    {filteredTasks.map((task) => (
                      <ListGroup.Item
                        key={task.id}
                        action
                        onClick={() => navigate(`/task/${task.id}`)}
                        className="py-3"
                      >
                        <div className="d-flex justify-content-between align-items-start">
                          <div className="flex-grow-1">
                            <div className="d-flex align-items-center gap-2 mb-2">
                              <span className="fs-5">{getCategoryIcon(task.category)}</span>
                              <h6 className="mb-0 fw-semibold">{task.title}</h6>
                              {getRiskBadge(task.riskAnalysis?.riskLevel, task.riskAnalysis?.riskScore)}
                            </div>
                            {task.description && (
                              <p className="text-muted small mb-2">
                                {task.description.length > 100
                                  ? task.description.substring(0, 100) + "..."
                                  : task.description}
                              </p>
                            )}
                            <div className="d-flex flex-wrap gap-3">
                              <small className="text-muted d-flex align-items-center gap-1">
                                <Calendar size={12} /> {formatDate(task.dueDate)}
                              </small>
                              <small className="text-muted d-flex align-items-center gap-1">
                                <Clock size={12} /> {getDaysRemaining(task.dueDate)}
                              </small>
                              {getPriorityBadge(task.priority)}
                            </div>
                          </div>
                          <div className="text-end ms-3">
                            {task.status !== "COMPLETED" && (
                              <Button
                                variant="success"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setTaskToComplete(task);
                                  setShowCompleteModal(true);
                                }}
                              >
                                <CheckCircle size={14} className="me-1" /> Complete
                              </Button>
                            )}
                            <Button
                              variant="outline-info"
                              size="sm"
                              className="mt-2"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleViewImpact(task);
                              }}
                            >
                              <Eye size={14} className="me-1" /> Impact
                            </Button>
                          </div>
                        </div>
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                ) : (
                  <div className="text-center py-5">
                    <Clock size={48} className="text-muted mb-3" />
                    <h6 className="text-muted">No tasks in this category</h6>
                    <Button
                      variant="primary"
                      onClick={() => navigate("/create-task")}
                      className="mt-2"
                    >
                      <Plus size={18} className="me-2" /> Create your first task
                    </Button>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* Modals */}
      <ImpactSimulationModal
        show={showImpactModal}
        onHide={() => setShowImpactModal(false)}
        task={selectedTask}
      />

      <Modal show={showCompleteModal} onHide={() => setShowCompleteModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Complete Task</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Mark "{taskToComplete?.title}" as completed?</p>
          <Form.Group className="mt-3">
            <Form.Label>Upload Proof (Optional)</Form.Label>
            <Form.Control
              type="file"
              onChange={(e) => setCompletionProof(e.target.files[0])}
            />
            <Form.Text className="text-muted">
              Upload screenshot or evidence of completion
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCompleteModal(false)}>
            Cancel
          </Button>
          <Button variant="success" onClick={handleCompleteTask}>
            <CheckCircle className="me-1" /> Complete Task
          </Button>
        </Modal.Footer>
      </Modal>

      <Modal
        show={showAchievementModal}
        onHide={() => setShowAchievementModal(false)}
        centered
        className="achievement-modal"
      >
        <Modal.Body className="text-center py-4">
          <div className="achievement-badge mb-3">
            <Award size={64} className="text-warning" />
          </div>
          <h4 className="fw-bold text-warning">Achievement Unlocked!</h4>
          <h5 className="mb-3">{newAchievement?.title}</h5>
          <p className="text-muted">{newAchievement?.description}</p>
          <div className="mt-3">
            <Badge bg="success" pill className="px-3 py-2">
              +{newAchievement?.xpReward} XP
            </Badge>
          </div>
        </Modal.Body>
        <Modal.Footer className="justify-content-center">
          <Button variant="primary" onClick={() => setShowAchievementModal(false)}>
            Awesome!
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default Dashboard;
