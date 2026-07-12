// src/components/dashboard/AchievementBadge.jsx
import React from "react";
import { OverlayTrigger, Tooltip } from "react-bootstrap";
import { Award, Star, Target, Zap } from "lucide-react";

const AchievementBadge = ({ achievement, size = "md" }) => {
  const getIcon = (type) => {
    switch (type) {
      case "star":
        return Star;
      case "target":
        return Target;
      case "zap":
        return Zap;
      default:
        return Award;
    }
  };

  const Icon = getIcon(achievement.icon);
  const sizeMap = { sm: 16, md: 24, lg: 32 };

  return (
    <OverlayTrigger
      placement="top"
      overlay={<Tooltip>{achievement.description}</Tooltip>}
    >
      <div className="position-relative d-inline-block">
        <Icon
          size={sizeMap[size]}
          className={`text-${achievement.color || "warning"}`}
          style={{ filter: achievement.unlocked ? "none" : "grayscale(1)" }}
        />
        {achievement.unlocked && achievement.level && (
          <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-primary">
            {achievement.level}
          </span>
        )}
      </div>
    </OverlayTrigger>
  );
};

export default AchievementBadge;
