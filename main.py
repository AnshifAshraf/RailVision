import cv2
import numpy as np
import time
import requests
from railvision_core.detector import RailVisionDetector
from railvision_core.video_processor import VideoStreamProcessor
from railvision_core.crowd_analyzer import CrowdAnalyzer

def main():
    print("Initializing RailVisionDetector...")
    detector = RailVisionDetector(model_version="yolov8n.pt")
    
    # Define a simple dummy ROI (e.g., a central polygon on a 640x640 screen)
    # This simulates focusing only on the train compartment's door/aisle area.
    roi_polygon = [
        [160, 160],
        [480, 160],
        [480, 480],
        [160, 480]
    ]
    
    print("Initializing VideoStreamProcessor on webcam 0...")
    # Initialize the video stream processor using local webcam (0)
    processor = VideoStreamProcessor(stream_url=0, roi=roi_polygon)
    
    print("Initializing CrowdAnalyzer...")
    analyzer = CrowdAnalyzer(max_capacity=5, alert_threshold=0.80)
    
    if not processor.start_stream():
        print("Failed to start video stream. Please check your webcam connection.")
        return

    print("Starting video stream. Press 'q' to exit.")
    
    last_api_post_time = time.time()
    
    while True:
        # Fetch the preprocessed frame from the processor
        frame = processor.get_processed_frame()
        if frame is None:
            print("Video stream ended or failed to read frame.")
            break
            
        # Pass the preprocessed frame to the detector
        headcount, bounding_boxes = detector.detect_passengers(frame)
        
        # Draw bounding boxes and labels on the frame
        for box in bounding_boxes:
            x1, y1, x2, y2 = map(int, box)
            
            # Draw the box rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add 'Person' label above the box
            cv2.putText(frame, "Person", (x1, max(15, y1 - 10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
        # Display the total headcount
        cv2.putText(frame, f"Headcount: {headcount}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    
        # Evaluate crowd density and alert status
        analysis = analyzer.evaluate_crowd(headcount)
        
        # Display Density %
        cv2.putText(frame, f"Density: {analysis['density']:.1f}%", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
                    
        # Visual indicator for overcrowding
        if analysis['alert_status']:
            cv2.putText(frame, "WARNING: OVERCROWDED", (100, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                    
        # Optional: draw the ROI polygon just to visualize what's not blacked out
        cv2.polylines(frame, [np.array(roi_polygon, np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)
        
        # Non-blocking 5-second timer to send data to the backend API
        current_time = time.time()
        if current_time - last_api_post_time >= 5.0:
            last_api_post_time = current_time
            
            payload = {
                "train_id": "TR-101",
                "carriage_id": "C-3",
                "headcount": headcount,
                "occupancy_percentage": analysis['density'],
                "alert_status": analysis['alert_status']
            }
            
            try:
                # Fire and forget request (with short timeout to not visibly lag the video loop)
                requests.post("http://127.0.0.1:8000/api/occupancy/", json=payload, timeout=0.1)
                # print("Data successfully sent to API.")
            except requests.exceptions.RequestException as e:
                # Catch connection errors or timeouts silently without breaking the video
                pass
                
        # Use OpenCV to display the live frame
        cv2.imshow("RailVision - Live Feed", frame)
        
        # Add a cv2.waitKey condition to break the loop when pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting stream...")
            break
            
    # Clean up and release resources
    processor.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
