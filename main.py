from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(title="Smart Agriculture Drone API")




drones = []
sensor_readings = []
missions = []
ai_results = []



class Location_Model(BaseModel):
    latitude: float
    longitude: float


class Drone_Model(BaseModel):
    drone_id: int
    name: str
    battery: int = Field(ge=0, le=100)
    status: str
    location: Location_Model



class Drone_Update_Model(BaseModel):
    name: str | None = None
    battery: int | None = Field(default=None, ge=0, le=100)
    status: str | None = None
    location: Location_Model | None = None



class Sensor_Data_Model(BaseModel):
    reading_id: int
    drone_id: int
    temperature: float
    humidity: float
    distance: float
    soil_moisture: float | None = None



class Mission_Model(BaseModel):
    mission_id: int
    drone_id: int
    field_name: str
    target_crop: str
    status: str = "pending"


class Mission_Update_Model(BaseModel):
    status: str



class AI_Result_Model(BaseModel):
    result_id: int
    mission_id: int
    drone_id: int
    disease_detected: bool
    disease_name: str | None = None
    confidence: float = Field(ge=0, le=1)
    location: Location_Model




def Find_Drone(drone_id: int):
    for drone in drones:
        if drone.drone_id == drone_id:
            return drone

    return None


def Find_Mission(mission_id: int):
    for mission in missions:
        if mission.mission_id == mission_id:
            return mission

    return None



@app.post("/drones")
def Create_Drone(drone_model: Drone_Model):

    if Find_Drone(drone_model.drone_id):
        raise HTTPException(
            status_code=409,
            detail="Drone ID already exists"
        )

    drones.append(drone_model)

    return {"message": "Drone added successfully!"}



@app.get("/drones")
def Get_All_Drones():
    return drones



@app.get("/drones/{drone_id}")
def Get_Drone(drone_id: int):

    drone = Find_Drone(drone_id)

    if drone is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found"
        )

    return drone



@app.put("/drones/{drone_id}")
def Update_Drone(drone_id: int, drone_model: Drone_Model):

    for index, drone in enumerate(drones):

        if drone.drone_id == drone_id:

            if drone_model.drone_id != drone_id:
                raise HTTPException(
                    status_code=400,
                    detail="Drone ID in URL and body must match"
                )

            drones[index] = drone_model

            return {"message": "Drone updated successfully!"}

    raise HTTPException(
        status_code=404,
        detail="Drone not found"
    )



@app.patch("/drones/{drone_id}")
def Patch_Drone(drone_id: int, updates: Drone_Update_Model):

    drone = Find_Drone(drone_id)

    if drone is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found"
        )

    updated_data = updates.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(drone, field, value)

    return {
        "message": "Drone partially updated successfully!",
        "drone": drone
    }



@app.delete("/drones/{drone_id}")
def Delete_Drone(drone_id: int):

    for index, drone in enumerate(drones):

        if drone.drone_id == drone_id:

            drones.pop(index)

            return {"message": "Drone deleted successfully!"}

    raise HTTPException(
        status_code=404,
        detail="Drone not found"
    )





@app.post("/sensor-data")
def Add_Sensor_Data(reading: Sensor_Data_Model):

    if Find_Drone(reading.drone_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found"
        )

    for old_reading in sensor_readings:
        if old_reading.reading_id == reading.reading_id:
            raise HTTPException(
                status_code=409,
                detail="Reading ID already exists"
            )

    sensor_readings.append(reading)

    return {"message": "Sensor data received successfully!"}



@app.get("/sensor-data")
def Get_All_Sensor_Data():
    return sensor_readings



@app.get("/sensor-data/drone/{drone_id}")
def Get_Drone_Sensor_Data(drone_id: int):

    if Find_Drone(drone_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found"
        )

    results = []

    for reading in sensor_readings:
        if reading.drone_id == drone_id:
            results.append(reading)

    return results



@app.post("/missions")
def Create_Mission(mission: Mission_Model):

    if Find_Drone(mission.drone_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found"
        )

    for old_mission in missions:
        if old_mission.mission_id == mission.mission_id:
            raise HTTPException(
                status_code=409,
                detail="Mission ID already exists"
            )

    missions.append(mission)

    return {"message": "Mission created successfully!"}



@app.get("/missions")
def Get_All_Missions():
    return missions



@app.get("/missions/{mission_id}")
def Get_Mission(mission_id: int):

    mission = Find_Mission(mission_id)

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    return mission



@app.patch("/missions/{mission_id}")
def Update_Mission_Status(
    mission_id: int,
    updates: Mission_Update_Model
):

    mission = Find_Mission(mission_id)

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    mission.status = updates.status

    return {
        "message": "Mission status updated successfully!",
        "mission": mission
    }



@app.post("/ai-results")
def Add_AI_Result(result: AI_Result_Model):

    if Find_Drone(result.drone_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found"
        )

    mission = Find_Mission(result.mission_id)

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    if mission.drone_id != result.drone_id:
        raise HTTPException(
            status_code=400,
            detail="Mission does not belong to this drone"
        )

    for old_result in ai_results:
        if old_result.result_id == result.result_id:
            raise HTTPException(
                status_code=409,
                detail="Result ID already exists"
            )

    ai_results.append(result)

    return {"message": "AI result received successfully!"}



@app.get("/ai-results")
def Get_All_AI_Results():
    return ai_results


@app.get("/ai-results/mission/{mission_id}")
def Get_Mission_AI_Results(mission_id: int):

    if Find_Mission(mission_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    results = []

    for result in ai_results:
        if result.mission_id == mission_id:
            results.append(result)

    return results