from model.trainer import ModelTrainer
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    trainer = ModelTrainer()
    metrics = trainer.train()
    print("Training complete!")
    print("Metrics:", metrics)
