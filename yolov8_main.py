"""Main entry point for YOLOv8 people counting using clean architecture."""

import argparse
import logging
from yolov8.core.processor import VideoProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format="[INFO] %(message)s")
log = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="YOLOv8 People Counter")
    parser.add_argument("-i", "--input", type=int, default=0,
                       help="Configuration input ID (default: 0)")
    parser.add_argument("--model", type=str, default="yolov8m.pt",
                       help="Path to YOLO model file (default: yolov8m.pt)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        log.info("Verbose logging enabled")
    
    log.info(f"Starting YOLOv8 People Counter with config ID: {args.input}")
    log.info(f"Using model: {args.model}")
    
    try:
        # Initialize and run the video processor
        processor = VideoProcessor(config_id=args.input)
        
        # Override model if specified
        if args.model != "yolov8m.pt":
            if processor.detector.switch_model(args.model):
                log.info(f"Switched to model: {args.model}")
            else:
                log.warning(f"Failed to switch to model: {args.model}, using default")
        
        # Run the processor
        processor.run()
        
    except KeyboardInterrupt:
        log.info("Application interrupted by user")
    except Exception as e:
        log.error(f"Application error: {e}")
        raise
    finally:
        log.info("Application shutdown complete")


if __name__ == "__main__":
    main()