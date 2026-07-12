import logging

from app.training import (
    train_deadline_model,
    train_failure_model,
    train_impact_model,
    train_intake_model,
    train_postanalysis_model,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("ai-service.train.all")


def main():
    logger.info("Training failure risk model...")
    logger.info(train_failure_model.train())

    logger.info("Training impact severity model...")
    logger.info(train_impact_model.train())

    logger.info("Training post-analysis cause model...")
    logger.info(train_postanalysis_model.train())

    logger.info("Training smart-intake NLP models...")
    logger.info(train_intake_model.train())

    logger.info("Training deadline-type NLP model...")
    logger.info(train_deadline_model.train())

    logger.info("All models trained and saved successfully.")


if __name__ == "__main__":
    main()
