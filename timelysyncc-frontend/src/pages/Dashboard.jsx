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
    if (!riskLevel || riskLevel === "SAFE") return null;
    const config = {
      CRITICAL: { bg: "danger", icon: AlertTriangle, text: "Critical" },
      WARNING: { bg: "warning", icon: AlertTriangle, text: "Warning" },
    };
    const { bg, icon: Icon, text } = config[riskLevel] || config.WARNING;
    return (
      <Badge bg={bg} pill className="dash-icon-text px-2 py-1 flex-shrink-0">
        <Icon size={12} />
        <span>{text}</span>
        {riskScore !== undefined && riskScore !== null && (
          <span>({riskScore}%)</span>
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
      <Badge bg={bg} pill className="px-2 py-1 dash-meta flex-shrink-0">
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
  const showSidebar =
    (failurePredictions && failurePredictions.length > 0) || highRiskTasks.length > 0;

  return (
    <>
      <Container className="dashboard">
        {/* Header */}
        <Row className="dash-section g-3">
          <Col xs={12}>
            <div className="dash-header-bar d-flex justify-content-between">
              <div className="min-w-0">
                <h2 className="text-primary dash-page-title text-break mb-1">
                  Welcome back, {user?.name || "User"}! 👋
                </h2>
                <p className="text-muted dash-page-subtitle mb-0">
                  {new Date().toLocaleDateString("en-US", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>
              <div className="dash-header-actions flex-shrink-0">
                <Button
                  variant="outline-primary"
                  className="dash-btn-icon dash-header-btn"
                  onClick={() => navigate("/create-task")}
                >
                  <Plus size={16} />
                  Manual Add
                </Button>
                <Button
                  variant="primary"
                  className="dash-btn-icon dash-header-btn"
                  onClick={() => navigate("/create-task?smart=true")}
                >
                  <Sparkles size={16} />
                  Smart Intake
                </Button>
              </div>
            </div>
          </Col>
        </Row>

        {/* User Stats Bar — 12 */}
        <Row className="dash-section g-3">
          <Col xs={12}>
            <Card className="shadow-sm border-0 dash-hero-card text-white">
              <Card.Body className="p-3">
                <div className="dash-hero-row d-flex justify-content-between align-items-center flex-wrap gap-3">
                  <div className="d-flex align-items-center gap-3 min-w-0">
                    <div className="dash-hero-icon rounded-circle dash-icon-wrap flex-shrink-0">
                      <Activity size={20} />
                    </div>
                    <div className="min-w-0">
                      <small className="dash-hero-muted dash-meta d-block">
                        Level {userStats.level}
                      </small>
                      <h5 className="text-white dash-card-title text-truncate">
                        {userStats.xp} / {userStats.nextLevelXp} XP
                      </h5>
                      <ProgressBar
                        now={(userStats.xp / (userStats.nextLevelXp || 1)) * 100}
                        className="dash-xp-progress"
                      />
                    </div>
                  </div>
                  <div className="dash-hero-metrics d-flex align-items-stretch">
                    <div className="dash-hero-metric text-center">
                      <div className="d-flex justify-content-center mb-2">
                        <Award size={16} />
                      </div>
                      <div className="text-white">
                        <strong className="dash-body d-block">
                          {userStats.achievements?.length || 0}
                        </strong>
                        <small className="d-block dash-hero-muted dash-meta">Achievements</small>
                      </div>
                    </div>
                    <div className="dash-hero-metric text-center">
                      <div className="d-flex justify-content-center mb-2">
                        <Star size={16} className="dash-hero-accent" />
                      </div>
                      <div className="text-white">
                        <strong className="dash-body d-block">{userStats.streak}</strong>
                        <small className="d-block dash-hero-muted dash-meta">Day Streak</small>
                      </div>
                    </div>
                    <div className="dash-hero-metric text-center">
                      <div className="d-flex justify-content-center mb-2">
                        <Gift size={16} />
                      </div>
                      <div className="text-white">
                        <strong className="dash-body d-block">{userStats.coins}</strong>
                        <small className="d-block dash-hero-muted dash-meta">Coins</small>
                      </div>
                    </div>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Cognitive Load Warning — 12 */}
        {cognitiveLoad?.level === "HIGH" && (
          <Row className="dash-section g-3">
            <Col xs={12}>
              <CognitiveLoadWarning
                activeCount={cognitiveLoad.activeCount}
                warningMessage={`You have ${cognitiveLoad.highPriorityCount} high-priority tasks among ${cognitiveLoad.activeCount} active tasks. Consider rescheduling or delegating some.`}
                maxCapacity={10}
                onViewTasks={() => setFilterType("ALL")}
                onPrioritize={() => setFilterType("HIGH_RISK")}
              />
            </Col>
          </Row>
        )}

        {/* Stats Cards — 3 + 3 + 3 + 3 */}
        <Row className="dash-section g-3">
          <Col xs={12} sm={6} lg={3}>
            <Card className="shadow-sm h-100 stat-card stat-card--primary">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start gap-2">
                  <div className="min-w-0">
                    <p className="dash-stat-label">Total Tasks</p>
                    <h2 className="dash-stat-value">{tasks.length}</h2>
                    <small className="dash-meta text-muted d-block text-truncate">
                      {stats.active} active · {stats.completed} completed
                    </small>
                  </div>
                  <div className="dash-icon-wrap stat-card__icon flex-shrink-0">
                    <Calendar size={20} />
                  </div>
                </div>
                <div className="stat-card-footer">
                  <ProgressBar
                    now={
                      tasks.length
                        ? Math.round((stats.active / tasks.length) * 100)
                        : 0
                    }
                  />
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={12} sm={6} lg={3}>
            <Card className="shadow-sm h-100 stat-card stat-card--success">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start gap-2">
                  <div className="min-w-0">
                    <p className="dash-stat-label">Completion Rate</p>
                    <h2 className="dash-stat-value">{completionRate}%</h2>
                    <small className="dash-meta text-muted d-block text-truncate">
                      {stats.completed} / {tasks.length} tasks
                    </small>
                  </div>
                  <div className="dash-icon-wrap stat-card__icon flex-shrink-0">
                    <CheckCircle size={20} />
                  </div>
                </div>
                <div className="stat-card-footer">
                  <ProgressBar now={completionRate} />
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={12} sm={6} lg={3}>
            <Card className="shadow-sm h-100 stat-card stat-card--warning">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start gap-2">
                  <div className="min-w-0">
                    <p className="dash-stat-label">On-Time Rate</p>
                    <h2 className="dash-stat-value">{onTimeRate}%</h2>
                    <small className="dash-meta text-muted d-block text-truncate">
                      Completed before deadline
                    </small>
                  </div>
                  <div className="dash-icon-wrap stat-card__icon flex-shrink-0">
                    <Clock size={20} />
                  </div>
                </div>
                <div className="stat-card-footer">
                  <ProgressBar now={onTimeRate} />
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col xs={12} sm={6} lg={3}>
            <Card className="shadow-sm h-100 stat-card stat-card--info">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start gap-2">
                  <div className="min-w-0">
                    <p className="dash-stat-label">Avg Risk Score</p>
                    <h2 className="dash-stat-value">{avgRiskScore}%</h2>
                    <small className="dash-meta text-muted d-block text-truncate">
                      {highRiskTasks.length} high risk tasks
                    </small>
                  </div>
                  <div className="dash-icon-wrap stat-card__icon flex-shrink-0">
                    <Shield size={20} />
                  </div>
                </div>
                <div className="stat-card-footer">
                  <ProgressBar now={avgRiskScore} />
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Search, sort, and filters — single toolbar row */}
        <Row className="dash-section g-3">
          <Col xs={12}>
            <div className="dash-toolbar">
              <InputGroup className="dash-toolbar-control dash-toolbar-search">
                <InputGroup.Text className="bg-white border-end-0 d-inline-flex align-items-center">
                  <Search size={16} className="text-muted" />
                </InputGroup.Text>
                <Form.Control
                  type="text"
                  placeholder="Search tasks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="border-start-0 dash-body"
                />
                {searchTerm && (
                  <Button
                    variant="outline-secondary"
                    className="dash-btn-icon"
                    onClick={() => setSearchTerm("")}
                  >
                    <X size={16} />
                  </Button>
                )}
              </InputGroup>

              <Dropdown className="dash-toolbar-sort">
                <Dropdown.Toggle
                  variant="outline-secondary"
                  className="dash-btn-icon dash-toolbar-control w-100"
                >
                  <BarChart3 size={14} />
                  <span className="text-truncate">
                    Sort:{" "}
                    {sortBy === "dueDate"
                      ? "Due Date"
                      : sortBy === "riskScore"
                        ? "Risk"
                        : "Priority"}
                  </span>
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={() => setSortBy("dueDate")}>Due Date</Dropdown.Item>
                  <Dropdown.Item onClick={() => setSortBy("riskScore")}>Risk Score</Dropdown.Item>
                  <Dropdown.Item onClick={() => setSortBy("priority")}>Priority</Dropdown.Item>
                  <Dropdown.Divider />
                  <Dropdown.Item
                    onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                  >
                    Toggle Order ({sortOrder === "asc" ? "Ascending" : "Descending"})
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>

              <div className="dash-filter-bar">
                {["ALL", "TODAY", "UPCOMING", "OVERDUE", "HIGH_RISK", "COMPLETED"].map((type) => {
                  const filterClass = {
                    ALL: "filter-chip filter-chip--primary",
                    TODAY: "filter-chip filter-chip--primary",
                    UPCOMING: "filter-chip filter-chip--primary",
                    OVERDUE: "filter-chip filter-chip--danger",
                    HIGH_RISK: "filter-chip filter-chip--warning",
                    COMPLETED: "filter-chip filter-chip--success",
                  }[type];
                  const isActive = filterType === type;
                  return (
                    <Button
                      key={type}
                      variant="outline-secondary"
                      size="sm"
                      className={`dash-btn-icon ${filterClass}${isActive ? " is-active" : ""}`}
                      onClick={() => setFilterType(type)}
                    >
                      {type === "ALL" && "All Active"}
                      {type === "TODAY" && `Today (${getFilterCount("TODAY")})`}
                      {type === "UPCOMING" && `Upcoming (${getFilterCount("UPCOMING")})`}
                      {type === "OVERDUE" && `Overdue (${getFilterCount("OVERDUE")})`}
                      {type === "HIGH_RISK" && `High Risk (${getFilterCount("HIGH_RISK")})`}
                      {type === "COMPLETED" && `Completed (${getFilterCount("COMPLETED")})`}
                    </Button>
                  );
                })}
              </div>
            </div>
          </Col>
        </Row>

        {/* Main Content — 4 + 8 (full width when sidebar empty) */}
        <Row className="g-3 align-items-start">
          {showSidebar && (
            <Col xs={12} lg={4} className="d-flex flex-column gap-3">
              <FailurePredictionCard predictions={failurePredictions} />

              {highRiskTasks.length > 0 && (
                <Card className="shadow-sm mb-0 dash-alert-card">
                  <Card.Header className="dash-alert-card__header text-white dash-card-header">
                    <div className="d-flex align-items-center gap-2">
                      <AlertOctagon size={16} className="flex-shrink-0" />
                      <h6 className="mb-0 dash-card-title text-truncate">Critical Alerts</h6>
                      <Badge bg="light" text="dark" pill className="ms-auto flex-shrink-0">
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
                        className="dash-list-item"
                      >
                        <div className="d-flex justify-content-between align-items-center gap-2">
                          <div className="min-w-0 flex-grow-1">
                            <div className="d-flex align-items-center gap-2 mb-2 min-w-0">
                              <span className="lh-1 flex-shrink-0">
                                {getCategoryIcon(task.category)}
                              </span>
                              <span className="fw-semibold dash-body text-truncate">
                                {task.title}
                              </span>
                            </div>
                            <div className="d-flex flex-wrap gap-2 gap-md-3 dash-meta text-muted">
                              <span className="text-nowrap">Due: {formatDate(task.dueDate)}</span>
                              <span className="text-danger text-nowrap">
                                {getDaysRemaining(task.dueDate)}
                              </span>
                            </div>
                          </div>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            className="dash-btn-icon flex-shrink-0"
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
          )}

          <Col xs={12} lg={showSidebar ? 8 : 12}>
            <Card className="shadow-sm h-100 dash-tasks-card">
              <Card.Header className="d-flex justify-content-between align-items-center dash-card-header gap-2">
                <div className="min-w-0">
                  <h5 className="dash-section-title text-truncate">
                    {filterType === "ALL" && "Active Tasks"}
                    {filterType === "TODAY" && "Today's Tasks"}
                    {filterType === "UPCOMING" && "Upcoming Tasks"}
                    {filterType === "OVERDUE" && "Overdue Tasks"}
                    {filterType === "HIGH_RISK" && "High Risk Tasks"}
                    {filterType === "COMPLETED" && "Completed Tasks"}
                  </h5>
                  <small className="text-muted dash-meta">
                    {filteredTasks.length}{" "}
                    {filteredTasks.length === 1 ? "task" : "tasks"} found
                  </small>
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {filteredTasks.length > 0 ? (
                  <ListGroup variant="flush">
                    {filteredTasks.map((task) => (
                      <ListGroup.Item
                        key={task.id}
                        action
                        onClick={() => navigate(`/task/${task.id}`)}
                        className="dash-list-item"
                      >
                        <div className="dash-task-row d-flex justify-content-between align-items-start gap-3">
                          <div className="flex-grow-1 min-w-0">
                            <div className="d-flex align-items-start gap-2 mb-2">
                              <span className="lh-1 fs-5 flex-shrink-0 mt-1">
                                {getCategoryIcon(task.category)}
                              </span>
                              <div className="min-w-0 flex-grow-1">
                                <div className="d-flex align-items-center flex-wrap gap-2">
                                  <h6 className="dash-card-title mb-0">{task.title}</h6>
                                  {getRiskBadge(
                                    task.riskAnalysis?.riskLevel,
                                    task.riskAnalysis?.riskScore,
                                  )}
                                  {getPriorityBadge(task.priority)}
                                </div>
                              </div>
                            </div>
                            {task.description && (
                              <p className="text-muted dash-body mb-2 dash-task-desc">
                                {task.description.length > 100
                                  ? task.description.substring(0, 100) + "..."
                                  : task.description}
                              </p>
                            )}
                            <div className="d-flex flex-wrap gap-2 gap-md-3 align-items-center">
                              <small className="text-muted dash-icon-text dash-meta">
                                <Calendar size={12} />
                                {formatDate(task.dueDate)}
                              </small>
                              <small className="text-muted dash-icon-text dash-meta">
                                <Clock size={12} />
                                {getDaysRemaining(task.dueDate)}
                              </small>
                            </div>
                          </div>
                          <div className="dash-action-stack">
                            {task.status !== "COMPLETED" && (
                              <Button
                                variant="success"
                                size="sm"
                                className="dash-btn-icon"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setTaskToComplete(task);
                                  setShowCompleteModal(true);
                                }}
                              >
                                <CheckCircle size={14} />
                                Complete
                              </Button>
                            )}
                            <Button
                              variant="outline-info"
                              size="sm"
                              className="dash-btn-icon"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleViewImpact(task);
                              }}
                            >
                              <Eye size={14} />
                              Impact
                            </Button>
                          </div>
                        </div>
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                ) : (
                  <div className="text-center py-5 px-3">
                    <Clock size={48} className="text-muted mb-3" />
                    <h6 className="text-muted dash-card-title mb-2">
                      {filterType === "ALL" && "No active tasks"}
                      {filterType === "TODAY" && "Nothing due today"}
                      {filterType === "UPCOMING" && "No upcoming tasks"}
                      {filterType === "OVERDUE" && "No overdue tasks"}
                      {filterType === "HIGH_RISK" && "No high-risk tasks"}
                      {filterType === "COMPLETED" && "No completed tasks yet"}
                    </h6>
                    {(filterType === "ALL" || filterType === "COMPLETED") && (
                      <Button
                        variant="primary"
                        className="dash-btn-icon mt-2"
                        onClick={() => navigate("/create-task")}
                      >
                        <Plus size={16} />
                        Create a task
                      </Button>
                    )}
                    {filterType !== "ALL" && filterType !== "COMPLETED" && (
                      <Button
                        variant="outline-primary"
                        className="dash-btn-icon mt-2"
                        onClick={() => setFilterType("ALL")}
                      >
                        View all active
                      </Button>
                    )}
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
          <Button variant="success" className="dash-btn-icon" onClick={handleCompleteTask}>
            <CheckCircle size={16} /> Complete Task
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
