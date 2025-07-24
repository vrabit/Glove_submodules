# Drone Final Project

This repository contains all files necessary for the final drone project, including firmware, data collection utilities, 3D models, and machine learning components.
Project Structure

📦 DroneFinalProject

   - Top-level directory containing all project components necessary to fly the drone.

📁 GloveCases

   - Contains various 3D case models for the Glove 2 prototype.

🛠️ GloveUtility

Includes:

   - Scripts for data collection

   - Collected gesture data

🤖 GroupSimulation

Integrates both the drone control system and the hand gesture recognition component into a final working simulation.
🔧 GloveFlexTest

Firmware for the NUCLEO-L432KC microcontroller. Outputs:

   - 5 resistance values per finger

   - 3 gyroscope values: roll, yaw, and pitch

🧠 drones_ML

Jupyter Notebook-based project using the collected data to:

   - Train machine learning models

   - Predict hand gestures based on input signals
