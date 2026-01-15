# FTCLib Vision

FTCLib integrates with EasyOpenCV to provide computer vision capabilities for FTC robots, including pre-built pipelines and easy camera setup.

## Imports

```java
// FTCLib Vision
import com.arcrobotics.ftclib.vision.UGContourRingPipeline;

// EasyOpenCV (included with FTC SDK 8.2+)
import org.openftc.easyopencv.OpenCvCamera;
import org.openftc.easyopencv.OpenCvCameraFactory;
import org.openftc.easyopencv.OpenCvCameraRotation;
import org.openftc.easyopencv.OpenCvInternalCamera;
import org.openftc.easyopencv.OpenCvWebcam;
import org.openftc.easyopencv.OpenCvPipeline;

// OpenCV
import org.opencv.core.Mat;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.imgproc.Imgproc;
```

## Camera Setup

### Internal Camera (Phone Camera)

```java
int cameraMonitorViewId = hardwareMap.appContext.getResources()
    .getIdentifier("cameraMonitorViewId", "id", hardwareMap.appContext.getPackageName());

OpenCvInternalCamera phoneCam = OpenCvCameraFactory.getInstance()
    .createInternalCamera(OpenCvInternalCamera.CameraDirection.BACK, cameraMonitorViewId);
```

### External Webcam

```java
int cameraMonitorViewId = hardwareMap.appContext.getResources()
    .getIdentifier("cameraMonitorViewId", "id", hardwareMap.appContext.getPackageName());

OpenCvWebcam webcam = OpenCvCameraFactory.getInstance()
    .createWebcam(
        hardwareMap.get(WebcamName.class, "Webcam 1"),
        cameraMonitorViewId
    );
```

### Without Monitor View

```java
// No preview on Driver Station
OpenCvWebcam webcam = OpenCvCameraFactory.getInstance()
    .createWebcam(hardwareMap.get(WebcamName.class, "Webcam 1"));
```

## Starting the Camera

```java
// Create pipeline
MyPipeline pipeline = new MyPipeline();

// Set pipeline before opening
camera.setPipeline(pipeline);

// Open camera asynchronously
camera.openCameraDeviceAsync(new OpenCvCamera.AsyncCameraOpenListener() {
    @Override
    public void onOpened() {
        // Start streaming when camera opens
        camera.startStreaming(320, 240, OpenCvCameraRotation.UPRIGHT);
    }

    @Override
    public void onError(int errorCode) {
        telemetry.addData("Camera Error", errorCode);
        telemetry.update();
    }
});
```

### Stream Resolutions

```java
// Common resolutions
camera.startStreaming(320, 240, ...);   // Low - faster processing
camera.startStreaming(640, 480, ...);   // Medium
camera.startStreaming(1280, 720, ...);  // High - slower processing
```

### Camera Rotation

```java
OpenCvCameraRotation.UPRIGHT
OpenCvCameraRotation.UPSIDE_DOWN
OpenCvCameraRotation.SIDEWAYS_LEFT
OpenCvCameraRotation.SIDEWAYS_RIGHT
```

## Creating Pipelines

### Basic Pipeline Structure

```java
public class MyPipeline extends OpenCvPipeline {

    // Detection results (accessed from OpMode)
    private volatile boolean objectDetected = false;
    private volatile Point objectCenter = new Point();

    @Override
    public Mat processFrame(Mat input) {
        // Process the frame
        // input is the camera image in BGR format

        // Your detection logic here...

        // Return the (optionally annotated) frame
        return input;
    }

    // Getters for OpMode to access results
    public boolean isObjectDetected() {
        return objectDetected;
    }

    public Point getObjectCenter() {
        return objectCenter;
    }
}
```

### Color Detection Pipeline

```java
public class ColorDetectionPipeline extends OpenCvPipeline {
    private volatile boolean detected = false;
    private volatile Rect boundingBox = new Rect();

    // HSV color range for detection
    private Scalar lowerBound = new Scalar(100, 100, 100);  // Blue lower
    private Scalar upperBound = new Scalar(130, 255, 255);  // Blue upper

    private Mat hsv = new Mat();
    private Mat mask = new Mat();
    private Mat hierarchy = new Mat();

    @Override
    public Mat processFrame(Mat input) {
        // Convert to HSV
        Imgproc.cvtColor(input, hsv, Imgproc.COLOR_RGB2HSV);

        // Create mask for color range
        Core.inRange(hsv, lowerBound, upperBound, mask);

        // Find contours
        List<MatOfPoint> contours = new ArrayList<>();
        Imgproc.findContours(mask, contours, hierarchy,
            Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE);

        // Find largest contour
        double maxArea = 0;
        Rect largestRect = new Rect();

        for (MatOfPoint contour : contours) {
            double area = Imgproc.contourArea(contour);
            if (area > maxArea && area > 500) {  // Minimum area threshold
                maxArea = area;
                largestRect = Imgproc.boundingRect(contour);
            }
        }

        detected = maxArea > 0;
        boundingBox = largestRect;

        // Draw detection on frame
        if (detected) {
            Imgproc.rectangle(input, boundingBox, new Scalar(0, 255, 0), 2);
        }

        return input;
    }

    public boolean isDetected() {
        return detected;
    }

    public Rect getBoundingBox() {
        return boundingBox;
    }

    public Point getCenter() {
        return new Point(
            boundingBox.x + boundingBox.width / 2.0,
            boundingBox.y + boundingBox.height / 2.0
        );
    }

    // Allow changing color at runtime
    public void setColorRange(Scalar lower, Scalar upper) {
        this.lowerBound = lower;
        this.upperBound = upper;
    }
}
```

### Region-Based Detection Pipeline

```java
public class RegionPipeline extends OpenCvPipeline {
    public enum Position { LEFT, CENTER, RIGHT }
    private volatile Position position = Position.CENTER;

    // Define regions of interest
    private static final Point REGION1_TOPLEFT = new Point(0, 100);
    private static final Point REGION2_TOPLEFT = new Point(110, 100);
    private static final Point REGION3_TOPLEFT = new Point(220, 100);
    private static final int REGION_WIDTH = 100;
    private static final int REGION_HEIGHT = 80;

    private Mat region1, region2, region3;
    private Mat yCbCr = new Mat();
    private Mat Cb = new Mat();

    @Override
    public void init(Mat firstFrame) {
        // Called once when pipeline starts
        inputToCb(firstFrame);

        region1 = Cb.submat(new Rect(
            (int) REGION1_TOPLEFT.x, (int) REGION1_TOPLEFT.y,
            REGION_WIDTH, REGION_HEIGHT));
        region2 = Cb.submat(new Rect(
            (int) REGION2_TOPLEFT.x, (int) REGION2_TOPLEFT.y,
            REGION_WIDTH, REGION_HEIGHT));
        region3 = Cb.submat(new Rect(
            (int) REGION3_TOPLEFT.x, (int) REGION3_TOPLEFT.y,
            REGION_WIDTH, REGION_HEIGHT));
    }

    @Override
    public Mat processFrame(Mat input) {
        inputToCb(input);

        // Calculate average color in each region
        int avg1 = (int) Core.mean(region1).val[0];
        int avg2 = (int) Core.mean(region2).val[0];
        int avg3 = (int) Core.mean(region3).val[0];

        // Find brightest region (most yellow/orange in Cb channel)
        int max = Math.max(Math.max(avg1, avg2), avg3);

        if (max == avg1) {
            position = Position.LEFT;
        } else if (max == avg2) {
            position = Position.CENTER;
        } else {
            position = Position.RIGHT;
        }

        // Draw regions
        Imgproc.rectangle(input,
            REGION1_TOPLEFT,
            new Point(REGION1_TOPLEFT.x + REGION_WIDTH, REGION1_TOPLEFT.y + REGION_HEIGHT),
            position == Position.LEFT ? new Scalar(0, 255, 0) : new Scalar(255, 0, 0), 2);

        // ... draw other regions similarly

        return input;
    }

    private void inputToCb(Mat input) {
        Imgproc.cvtColor(input, yCbCr, Imgproc.COLOR_RGB2YCrCb);
        Core.extractChannel(yCbCr, Cb, 1);
    }

    public Position getPosition() {
        return position;
    }
}
```

## Using Vision in OpModes

### Autonomous with Vision

```java
@Autonomous(name = "Vision Auto")
public class VisionAuto extends CommandOpMode {
    private OpenCvWebcam webcam;
    private RegionPipeline pipeline;

    @Override
    public void initialize() {
        // Setup camera
        int cameraMonitorViewId = hardwareMap.appContext.getResources()
            .getIdentifier("cameraMonitorViewId", "id", hardwareMap.appContext.getPackageName());

        webcam = OpenCvCameraFactory.getInstance()
            .createWebcam(hardwareMap.get(WebcamName.class, "Webcam 1"), cameraMonitorViewId);

        pipeline = new RegionPipeline();
        webcam.setPipeline(pipeline);

        webcam.openCameraDeviceAsync(new OpenCvCamera.AsyncCameraOpenListener() {
            @Override
            public void onOpened() {
                webcam.startStreaming(320, 240, OpenCvCameraRotation.UPRIGHT);
            }

            @Override
            public void onError(int errorCode) {}
        });

        // Wait for detection during init
        while (!isStarted() && !isStopRequested()) {
            telemetry.addData("Position", pipeline.getPosition());
            telemetry.update();
            sleep(50);
        }

        // Stop streaming to save resources
        webcam.stopStreaming();

        // Schedule autonomous based on detection
        RegionPipeline.Position detected = pipeline.getPosition();

        switch (detected) {
            case LEFT:
                schedule(new LeftAutoCommand(drive));
                break;
            case CENTER:
                schedule(new CenterAutoCommand(drive));
                break;
            case RIGHT:
                schedule(new RightAutoCommand(drive));
                break;
        }
    }
}
```

### Continuous Vision in TeleOp

```java
@TeleOp(name = "Vision TeleOp")
public class VisionTeleOp extends CommandOpMode {
    private ColorDetectionPipeline pipeline;

    @Override
    public void initialize() {
        // ... camera setup ...

        pipeline = new ColorDetectionPipeline();

        // Create trigger based on detection
        Trigger objectDetected = new Trigger(pipeline::isDetected);

        objectDetected.whenActive(new InstantCommand(() -> {
            // Auto-aim or grab when object detected
            Point center = pipeline.getCenter();
            // Use center.x to adjust robot position
        }));
    }
}
```

## FTCLib Built-in Pipelines

### UGContourRingPipeline (Ultimate Goal)

Pre-built pipeline for ring stack detection.

```java
UGContourRingPipeline pipeline = new UGContourRingPipeline(
    telemetry,      // For debug output
    DEBUG           // Show processing steps
);

camera.setPipeline(pipeline);

// Get result
UGContourRingPipeline.Height height = pipeline.getHeight();
// Returns: ZERO, ONE, or FOUR
```

## Testing with EOCV-Sim

Test pipelines on your computer before deploying to robot.

1. Install EOCV-Sim from https://github.com/serivesmejia/EOCV-Sim
2. Copy your pipeline class to the simulator
3. Test with images or video
4. Copy back to robot code when working

## Anti-Patterns

### Bad: Blocking in pipeline

```java
@Override
public Mat processFrame(Mat input) {
    Thread.sleep(100);  // Never block!
    return input;
}
```

### Good: Fast processing

```java
@Override
public Mat processFrame(Mat input) {
    // Keep processing fast - runs every frame
    // Target < 33ms for 30fps
    return input;
}
```

### Bad: Creating Mats every frame

```java
@Override
public Mat processFrame(Mat input) {
    Mat hsv = new Mat();  // Memory leak!
    Imgproc.cvtColor(input, hsv, Imgproc.COLOR_RGB2HSV);
    return input;
}
```

### Good: Reuse Mats

```java
private Mat hsv = new Mat();  // Class field

@Override
public Mat processFrame(Mat input) {
    Imgproc.cvtColor(input, hsv, Imgproc.COLOR_RGB2HSV);
    return input;
}
```

### Bad: Not making results volatile

```java
private boolean detected;  // Not thread-safe!

@Override
public Mat processFrame(Mat input) {
    detected = true;  // Race condition
    return input;
}
```

### Good: Use volatile for cross-thread access

```java
private volatile boolean detected;  // Thread-safe

@Override
public Mat processFrame(Mat input) {
    detected = true;  // Safe to read from OpMode
    return input;
}
```

## HSV Color Reference

Common HSV ranges for FTC game pieces:

```java
// Red (wraps around 0/180)
new Scalar(0, 100, 100), new Scalar(10, 255, 255)     // Red low
new Scalar(160, 100, 100), new Scalar(180, 255, 255) // Red high

// Blue
new Scalar(100, 100, 100), new Scalar(130, 255, 255)

// Yellow
new Scalar(20, 100, 100), new Scalar(35, 255, 255)

// Green
new Scalar(40, 100, 100), new Scalar(80, 255, 255)

// Orange
new Scalar(10, 100, 100), new Scalar(25, 255, 255)

// Purple
new Scalar(130, 100, 100), new Scalar(160, 255, 255)
```

## Resources

- [EasyOpenCV GitHub](https://github.com/OpenFTC/EasyOpenCV)
- [EOCV-Sim](https://github.com/serivesmejia/EOCV-Sim)
- [OpenCV Documentation](https://docs.opencv.org/)
