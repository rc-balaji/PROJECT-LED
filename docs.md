# Request from Client
### 1. Login
**Endpoint**: `POST /login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "success": true,
  "user": {
    "email": "user@example.com"
  }
}
```

---


### 2. Get Device Information
**Endpoint**: `GET /device`

**Response**: 
```json
Array of device objects retrieved from the `static.json` file.
```
#### Sample
```
[
  {
    "IP": "192.168.4.1",
    "ID": "KT-1",
    "master_id": "STA-1"
  }
]
```

### 3. Get Device Information from Excel
**Endpoint**: `GET /device/excel`

**Response**:
Array of device objects retrieved from the `led_mac_data.xlsx` file.


#### Sample
```
[
    {
        "ID": "KT-1",
        "isMaster": true,
        "available": true
    },
    {
        "ID": "KT-2",
        "isMaster": false,
        "available": true
    }
]
```
---


### 4 . Create New Group
**Endpoint**: `POST /new/group`

**Request Body**:
```json
{
  "newGroupid": "group123",
  "newGroupDeviceId": "device123"
}
```

**Response**:
```json
{
  "message": "Group added successfully",
  "group": {
    "Group_id": "group123",
    "master_device_id": "device123",
    "racks": []
  }
}
```

###  5 . Delete Group
**Endpoint**: `POST /delete/group`

**Request Body**:
```json
{
  "groupId": "group123"
}
```

**Response**:
```json
{
  "message": "Group deleted successfully"
}
```

---


###  6 . Add New Rack to Group
**Endpoint**: `POST /new/rack`

**Request Body**:
```json
{
  "Groupid": "group123",
  "newWrackid": "rack123",
  "id": "device123"
}
```

**Response**:
```json
{
  "message": "Rack added successfully",
  "rack": {
    "rack_id": "rack123",
    "mac": [1, 2, 3, 4, 5, 6],
    "device_id": "device123",
    "bins": [...]
  }
}
```

###  7 . Delete Rack from Group
**Endpoint**: `POST /delete/rack`

**Request Body**:
```json
{
  "Groupid": "group123",
  "rackId": "rack123"
}
```

**Response**:
```json
{
  "message": "Rack deleted successfully",
  "rackId": "rack123"
}
```

---

### 8 . Get Bin Details
**Endpoint**: `GET /bin`

**Query Parameters**:
- `group_id`
- `rack_id`
- `bin_id`

**Response**: Details of the requested bin.

#### Sample
```
{
   "group_id": "STA-1",
    "rack_id": "111",
    "color": [
        255,
        255,
        255
    ],
    "led_pin": 12,
    "bin_id": "111_01",
    "button_pin": 13,
    "schedules": [],
    "enabled": true,
    "clicked": false,
}
```

### 9. Toggle Bin Clicked Status
**Endpoint**: `POST /bin/update/clicked`

**Request Body**:
```json
{
  "group_id": "group123",
  "rack_id": "rack123",
  "bin_id": "bin123"
}
```

**Response**: Updated bin object with new `clicked` status.

### 10 . Update Bin Schedule
**Endpoint**: `PUT /bin/update/schedule`

**Request Body**:
```json
{
  "group_id": "group123",
  "rack_id": "rack123",
  "bin_id": "bin123",
  "scheduled_index": 0,
  "current_enabled_status": true
}
```

**Response**: Updated bin schedule object.

---


### 11. Add New Schedule
**Endpoint**: `POST /new/schedule`

**Request Body**:
```json
{
  "group_id": "group123",
  "wrack_id": "rack123",
  "bin_id": "bin123",
  "new_schduled": {
    "time": "12:00",
    "color": [255, 0, 0],
    "enabled": true
  }
}
```

**Response**:
```json
{
  "message": "Schedule added successfully",
  "bin": {...}
}
```

### 12. Delete Schedule
**Endpoint**: `POST /delete/schedule`

**Request Body**:
```json
{
  "group_id": "group123",
  "wrack_id": "rack123",
  "bin_id": "bin123",
  "scheduleIndex": 0
}
```

**Response**:
```json
{
  "message": "Schedule deleted successfully",
  "bin": {...}
}
```

---


### 13 . Import Data from Excel
**Endpoint**: `POST /import`

**Request Body**: Form-data with file upload.

**Response**:
```json
{
  "message": "File imported and data updated successfully"
}
```

---

# Request from ESP32

### 1 . Get Current Time
**Endpoint**: `GET /get-time1`

**Response**:
```json
{
  "time": "2024-10-01T10:34:56.789Z"
}
```

---

### 2 . Update click event
**Endpoint**: `POST /click/update`

**Request Body**: 

```
    {
       "group_id": "group123",
       "rack_id": "rack123",
       "bin_idx": 0
     }


```

**Response**: `Data updated successfully`


---




# Communication Request to ESP32

### Note : Everything has the same port and end point and each master differentiate with their ip unique address

eg : http://192.168.4.1:8000/  



## Operations :-
**Operation Performs based on the 'operation' key in the request body**

### 1 .  **Click-Change**

#### Request Body
```json
{
  "group_id": "GR001",
  "rack_id": "RCK001",
  "bin_id": "BIN001",
  "operation": "click-change"
}
```

- **group_id**: The identifier for the group, e.g., `"GR001"`.
- **rack_id**: The identifier for the rack within the group, e.g., `"RCK001"`.
- **bin_id**: The identifier for the bin within the rack, e.g., `"BIN001"`.
- **operation**: The type of operation to perform, in this case, `"click-change"`.

This operation sends a request to update the `clicked` status of a specific bin.

---



### 3 . **Push-Schedule**

#### Request Body
```json
{
  "group_id": "GR001",
  "rack_id": "RCK001",
  "bin_id": "BIN001",
  "operation": "push",
  "new_schedule_time": "14:30",
  "color": [16, 32, 48]
}
```

- **group_id**: The identifier for the group, e.g., `"GR001"`.
- **rack_id**: The identifier for the rack, e.g., `"RCK001"`.
- **bin_id**: The identifier for the bin, e.g., `"BIN001"`.
- **operation**: The type of operation, in this case, `"push"`.
- **new_schedule_time**: The time to set for the new schedule, e.g., `"14:30"`.
- **color**: RGB array representing the LED color to use for this schedule, e.g., `[16, 32, 48]`.

This operation pushes a new schedule for the bin.

---

### 4. **Remove-Schedule**

#### Request Body
```json
{
  "group_id": "GR001",
  "rack_id": "RCK001",
  "bin_id": "BIN001",
  "operation": "remove-schedule",
  "scheduled_time": "14:30"
}
```

- **group_id**: The identifier for the group, e.g., `"GR001"`.
- **rack_id**: The identifier for the rack, e.g., `"RCK001"`.
- **bin_id**: The identifier for the bin, e.g., `"BIN001"`.
- **operation**: The type of operation to perform, in this case, `"remove-schedule"`.
- **scheduled_time**: The time of the schedule to be removed, e.g., `"14:30"`.

This operation removes an existing schedule from the bin.

---

### 5 . **Add-Rack**

#### Request Body
```json
{
  "group_id": "GR001",
  "new_rack_id": "RCK002",
  "mac": [176, 167, 50, 43, 142, 152],
  "operation": "add-rack"
}
```

- **group_id**: The identifier for the group, e.g., `"GR001"`.
- **new_rack_id**: The identifier for the new rack to be added, e.g., `"RCK002"`.
- **mac**: The MAC address of the new rack device, e.g., `[176, 167, 50, 43, 142, 152]`.
- **operation**: The type of operation, in this case, `"add-rack"`.

This operation adds a new rack to the group.

---

### 6 .  **Remove-Rack**

#### Request Body
```json
{
  "group_id": "GR001",
  "rack_id": "RCK001",
  "operation": "remove-rack"
}
```

- **group_id**: The identifier for the group, e.g., `"GR001"`.
- **rack_id**: The identifier for the rack to be removed, e.g., `"RCK001"`.
- **operation**: The type of operation, in this case, `"remove-rack"`.

This operation removes the specified rack from the group.

---

### 7 . **Schedule-Change**

#### Request Body
```json
{
  "group_id": "GR001",
  "rack_id": "RCK001",
  "bin_id": "BIN001",
  "operation": "schedule-change",
  "scheduled_index": 1,
  "current_enabled_status": true
}
```

- **group_id**: The identifier for the group, e.g., `"GR001"`.
- **rack_id**: The identifier for the rack, e.g., `"RCK001"`.
- **bin_id**: The identifier for the bin, e.g., `"BIN001"`.
- **operation**: The type of operation, in this case, `"schedule-change"`.
- **scheduled_index**: The index of the schedule being modified, e.g., `1`.
- **current_enabled_status**: A boolean indicating whether the schedule is enabled or disabled, e.g., `true`.

This operation updates the enabled status of a schedule.

---

### 8 : **Add-Master**

#### Request Body
```json
{
  "new_group_id": "GR002",
  "operation": "add-master"
}
```

- **new_group_id**: The identifier for the new group to be added, e.g., `"GR002"`.
- **operation**: The type of operation, in this case, `"add-master"`.

This operation adds a new master group.

---

### 9 : **Remove-Master**

#### Request Body
```json
{
  "group_id": "GR001",
  "operation": "remove-master"
}
```

- **group_id**: The identifier for the group to be removed, e.g., `"GR001"`.
- **operation**: The type of operation, in this case, `"remove-master"`.

This operation removes the master group.

---

