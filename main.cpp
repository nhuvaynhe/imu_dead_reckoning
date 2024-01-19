#include <iostream>
#include <iomanip>
#include <csignal>  // Include this for signal handling
#include "xdpchandler.h"

using namespace std;
XdpcHandler xdpcHandler;

int connectIMU();
void initLogfile();

// Global variable to control the main loop
volatile sig_atomic_t isRunning = true;

// Signal handler function
void signalHandler(int signum) {
    if (signum == SIGINT) {
        isRunning = false;
    }
}

void printVelocityIncrement(XsVector vel)
{
	cout << "X:" << right << setw(7) << fixed << setprecision(2) << vel.value(0)
		<< ", Y:" << right << setw(7) << fixed << setprecision(2) << vel.value(1)
		<< ", Z:" << right << setw(7) << fixed << setprecision(2) << vel.value(2)
		<< " | ";
}

void printOrientationIncrement(XsQuaternion quat)
{
	cout << "W:" << right << setw(7) << fixed << setprecision(2) << quat.w()
		<< ", X:" << right << setw(7) << fixed << setprecision(2) << quat.x()
		<< ", Y:" << right << setw(7) << fixed << setprecision(2) << quat.y()
		<< ", Z:" << right << setw(7) << fixed << setprecision(2) << quat.z();
}

//--------------------------------------------------------------------------------
int main(void)
{
	// Set the signal handler
    signal(SIGINT, signalHandler);

	bool isConnected = connectIMU();
	if (!(isConnected)) {
		printf("NOT CONNECTED");
		return -1;
	}

	initLogfile();
/*-------------------------------------------------
				SCAN PROCESS
-------------------------------------------------*/
	bool orientationResetDone = false;
	int64_t startTime = XsTime::timeStampNow();
	while (isRunning)
	{
		if (xdpcHandler.packetsAvailable())
		{
			cout << "\r";
			for (auto const& device : xdpcHandler.connectedDots())
			{
				// Retrieve a packet
				XsDataPacket packet = xdpcHandler.getNextPacket(device->bluetoothAddress());

				// Get dv
				if (packet.containsVelocityIncrement())
				{
					XsVector vel = packet.velocityIncrement();
					printVelocityIncrement();
				}

				// Get dq
				if (packet.containsOrientationIncrement())
				{
					XsQuaternion quat = packet.orientationIncrement();
					printOrientationIncrement();
				}
			}

			// Reset heading
			cout << flush;
			if (!orientationResetDone && (XsTime::timeStampNow() - startTime) > 5000) // Reset over 5s
			{
				for (auto const& device : xdpcHandler.connectedDots())
				{
					cout << endl << "Resetting heading for device " << device->bluetoothAddress() << ": ";
					if (device->resetOrientation(XRM_Heading))
						cout << "OK";
					else
						cout << "NOK: " << device->lastResultText();
				}
				cout << endl;
				orientationResetDone = true;
			}
		}
		XsTime::msleep(0);
	}
	cout << "\n" << string(83, '-') << "\n";
	cout << endl;

	for (auto const& device : xdpcHandler.connectedDots())
	{
		cout << endl << "Resetting heading to default for device " << device->bluetoothAddress() << ": ";
		if (device->resetOrientation(XRM_DefaultAlignment))
			cout << "OK";
		else
			cout << "NOK: " << device->lastResultText();
	}
	cout << endl << endl;

/*-------------------------------------------------
				STOP SCAN PROCESS
-------------------------------------------------*/
	cout << "Stopping measurement..." << endl;
	for (auto device : xdpcHandler.connectedDots())
	{
		if (!device->stopMeasurement())
			cout << "Failed to stop measurement.";

		if (!device->disableLogging())
			cout << "Failed to disable logging.";
	}

	xdpcHandler.cleanup();

	return 0;
}

/*-------------------------------------------------
				INITIALIZE PROCESS
-------------------------------------------------*/
int connectIMU()
{
	if (!xdpcHandler.initialize())
		return -1;

	xdpcHandler.scanForDots();	

	if (xdpcHandler.detectedDots().empty())
	{
		cout << "No Movella DOT device(s) found. Aborting." << endl;
		xdpcHandler.cleanup();
		return -1;
	}

	xdpcHandler.connectDots();

	if (xdpcHandler.connectedDots().empty())
	{
		cout << "Could not connect to any Movella DOT device(s). Aborting." << endl;
		xdpcHandler.cleanup();
		return -1;
	}

	return 1;
}

void initLogfile()
{
	for (auto& device : xdpcHandler.connectedDots())
	{		
		auto filterProfiles = device->getAvailableFilterProfiles();
		cout << filterProfiles.size() << " available filter profiles:" << endl;
		for (auto& f : filterProfiles)
			cout << f.label() << endl;

		cout << "Current profile: " << device->onboardFilterProfile().label() << endl;
		if (device->setOnboardFilterProfile(XsString("General")))
			cout << "Successfully set profile to General" << endl;
		else
			cout << "Setting filter profile failed!" << endl;

		cout << "Setting quaternion CSV output" << endl;
		device->setLogOptions(XsLogOptions::Quaternion);

		XsString logFileName = XsString("logfile_") << device->bluetoothAddress().replacedAll(":", "-") << ".csv";
		cout << "Enable logging to: " << logFileName.c_str() << endl;
		if (!device->enableLogging(logFileName))
			cout << "Failed to enable logging. Reason: " << device->lastResultText() << endl;

		cout << "Putting device into measurement mode." << endl;
		if (!device->startMeasurement(XsPayloadMode::DeltaQuantities))
		{
			cout << "Could not put device into measurement mode. Reason: " << device->lastResultText() << endl;
			continue;
		}
	}

	cout << "\nMain loop. Logging data for 10 seconds." << endl;
	cout << string(83, '-') << endl;

	// First printing some headers so we see which data belongs to which device
	for (auto const& device : xdpcHandler.connectedDots())
		cout << setw(42) << left << device->bluetoothAddress();
	cout << endl;
}