# HTTP Control Module

## Introduction

The HTTP Control module allows control of the TWCManager Tesla Wall Charger controller via an in-built HTTP web server.

The web-server is multi-threaded (ie, it can be managed by multiple clients simultaneously), but does not support HTTPS encryption. It listens on Port 8080. As of release v1.1.5, it does not currently have any configurable options (but will in the future).

### HTTP Control Module vs IPC Web Interface

There are two separate interfaces for managing TWCManager via web browser. These are:

   * WebIPC - The original web interface bundled with TWCManager
   * HTTPControl - The new in-built web interface
   
**Benefits of HTTPControl**

   * Tightly integrated with the TWCManager controller. Less development lead-time to add functions.

**Drawbacks of HTTPControl**

   * Does not support HTTPS encryption.

### Status

| Detail          | Value          |
| --------------- | -------------- |
| **Module Name** | HTTPControl    |
| **Module Type** | Status         |
| **Status**      | In Development |

## Configuration

The following table shows the available configuration parameters for the MQTT Control module.

| Parameter   | Value         |
| ----------- | ------------- |
| enabled     | *required* Boolean value, ```true``` or ```false```. Determines whether we will enable HTTP control. |
| listenPort | *optional* HTTP Web Server port. Defaults to port 8080. |

### JSON Configuration Example

```
"control": {
  "HTTP": {
    "enabled": true,
    "listenPort": 8080
  }
}
```

## Using the HTTP Web Interface

If you have enabled HTTPControl, access it via the specified port. For example if your TWCManager machine is 192.168.1.1 and listenPort is 8080, access the HTTP interface with the following URL:

<a href="http://192.168.1.1:8080/">http://192.168.1.1:8080/</a>

## Using the API Interface

The HTTPControl web server provides an API interface under the /api URL root. The following methods are used when interacting with the API interface:

   * GET requests for requesting information or parameters
   * POST requests for performing actions or providing data

The following API endpoints exist:

| Endpoint  | Method | Description                                       |
| --------- | ------ | ------------------------------------------------- |
| <a href="/docs/modules/control_HTTP_API/cancelChargeNow.md">cancelChargeNow</a> | POST | Cancels active chargeNow configuration        |
| <a href="/docs/modules/control_HTTP_API/chargeNow.md">chargeNow</a> | POST   | Instructs charger to start charging at specified rate |
| getConfig | GET    | Provides the current configuration                |
| getPolicy | GET    | Provides the policy configuration                 |
| getSlaveTWCs | GET | Provides a list of connected Slave TWCs and their state |
| getStatus | GET    | Provides the current status (Charge Rate, Policy) |
| sendStartCommand | POST | Sends the Start command to all Slave TWCs    |
| <a href="/docs/modules/control_HTTP_API/sendStopCommand.md">sendStopCommand</a>  | POST | Sends the Stop command to all Slave TWCs     |
| <a href="/docs/modules/control_HTTP_API/setScheduledChargingSettings.md">setScheduledChargingSettings</a>  | POST | Saves Scheduled Charging settings --> can be retrieved with getStatus |
