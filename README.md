# Hand Gesture Controlled Drone System

This repository contains the full scope of the "Hand Gesture Controlled Drone System" project, a senior design capstone demonstrating the seamless integration of hardware, firmware, and software to enable drone control through intuitive hand gestures. This project serves as a comprehensive example of interdisciplinary engineering, combining microcontroller programming, sensor integration, real-time data processing, machine learning, and robotic simulation/control.

---

## 🚀 Project Overview

The primary objective of this project was to develop a novel method for guiding a drone using hand gestures captured by a custom-built smart glove. It demonstrates how diverse engineering disciplines—including embedded systems, machine learning, and robotics—can converge to create an innovative, functional system. While designed for demonstration, the underlying principles could have applications for users who cannot operate traditional controllers or simply offer a unique way to interact with unmanned aerial vehicles.

---

## ✨ Key Features & Components

This project is structured into several interconnected components, each contributing to the overall functionality of the hand gesture-controlled drone system:

### `DroneFinalProject/`
   - The top-level directory encompassing all integrated components necessary for the complete drone control system.

### `GloveCases/`
   - Contains **3D models** for various prototypes of the custom **Glove 2**. These models were meticulously designed to ergonomically house the electronic components and ensure comfortable, accurate gesture capture.

### `🛠️ GloveUtility/`
* **Data Collection Scripts:** Python scripts developed for efficient, real-time acquisition of raw sensor data from the glove prototype.
* **Collected Gesture Data:** The raw and processed datasets derived from the glove sensors, crucial for training and validating the machine learning models.

### `GroupSimulation/`
   - This critical component integrates the entire system. It combines the drone control logic with the real-time hand gesture recognition module, providing a **fully functional simulation environment** (built in **Webots**) to demonstrate the project's end-to-end capabilities before deployment to a physical drone.

### `GloveFlexTest/`
* **Microcontroller Firmware:** Firmware developed for the **NUCLEO-L432KC microcontroller** embedded within the glove. This firmware is responsible for:
    * Reading **5 resistance values** (one per finger) from **Spectra Symbol Flex Sensors** based on finger curvature.
    * Acquiring **9-axis absolute orientation data** from the **BNO055 sensor**, specifically extracting gyroscope values (roll, pitch, yaw) for hand orientation.
    * Transmitting this consolidated sensor data for real-time gesture analysis.

### `drones_ML/`
* **Machine Learning Pipeline:** A **Jupyter Notebook-based project** dedicated to processing the collected gesture data. This section covers:
    * **Model Training:** Development and training of **SVM (Support Vector Machine) 1 vs. 1 Classifiers** to accurately classify hand gestures based on the complex sensor inputs.
        * Training Accuracy: $99.90\%$
        * Validation Accuracy: $99.90\%$
        * Testing Accuracy: $99.63\%$
    * **Gesture Prediction:** Implementation of algorithms to predict specific hand gestures in real-time from input signals, utilizing Python and the `scikit-learn` library.

---
## 🧠 Design & Implementation Highlights

This project required the careful integration of diverse hardware and software components, presenting several unique challenges and innovative solutions:

* **Sensor Integration & Firmware Development:** Firmware was written to precisely pull real-time data from the flex sensors and the BNO055 IMU via I2C, streaming it effectively using `asyncio` for asynchronous data handling.

* **Robust Data Collection Pipeline:** A custom Python script utilizing `asyncio` was developed to collect, format, and save sensor data from the prototype glove to CSV files, which were then used for machine learning model training.

* **Real-time Data Stream & Gesture-to-Command Translation:** A key challenge involved streaming live sensor data to the ML model for gesture recognition and then seamlessly relaying the recognized gestures to the drone control software. This was achieved by establishing a serial connection for glove data input and then using an `asyncio.open_connection` port for the ML script to communicate gesture commands to the asynchronous drone flight script.

* **Outlier Data Filtering for Reliable Control:** To prevent erroneous sensor readings or transient gesture misclassifications from affecting drone behavior, a `deque` (double-ended queue) was implemented. This queue held the last 10 predicted gesture values, and a gesture was only confirmed and sent to the drone control system once all 10 values in the deque were identical, ensuring robust and stable command execution.

* **Hybrid Gesture-Orientation Control:** The system uniquely combined a base gesture with hand orientation for specific drone movements, enabling nuanced control with a limited number of gestures:
    * **Gesture 3 (Forward/Back):** Drone moves forward or backward based on exceeding $\pm 90$ degrees of yaw (Z-axis) rotation of the hand.
    * **Gesture 5 (Left/Right Strafe):** Drone strafes left or right based on exceeding $\pm 90$ degrees of roll (X-axis) rotation of the hand.
    * **Gesture 0 (Yaw Rotation):** Drone rotates left or right based on exceeding $\pm 90$ degrees of yaw (Z-axis) rotation of the hand.
    * **Gesture 1 (Pitch Control):** Drone adjusts its pitch (forward/back tilt) based on exceeding $\pm 90$ degrees of pitch (Y-axis) rotation of the hand.
---
