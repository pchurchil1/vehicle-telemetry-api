from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.ecu import Ecu
from app.models.event import Event
from app.models.signal import Signal
from app.models.user import User
from app.models.vehicle import Vehicle


SEED_VIN = "1FTFW1RG0PFA12345"


def seed() -> None:
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(
                User(
                    username="admin",
                    password_hash=hash_password("password123"),
                    role="admin",
                    is_active=True,
                )
            )

        vehicle = db.query(Vehicle).filter(Vehicle.vin == SEED_VIN).first()
        created_vehicle = False
        if vehicle is None:
            vehicle = Vehicle(vin=SEED_VIN, make="Ford", model="F-150", year=2024)
            db.add(vehicle)
            db.flush()
            created_vehicle = True

        ecu = (
            db.query(Ecu)
            .filter(Ecu.vehicle_id == vehicle.id, Ecu.name == "ECM")
            .first()
        )
        if ecu is None:
            ecu = Ecu(vehicle_id=vehicle.id, name="ECM", supplier="Bosch")
            db.add(ecu)
            db.flush()

        signal = (
            db.query(Signal)
            .filter(Signal.vehicle_id == vehicle.id, Signal.name == "engine_rpm")
            .first()
        )
        if signal is None:
            signal = Signal(
                vehicle_id=vehicle.id,
                ecu_id=ecu.id,
                name="engine_rpm",
                unit="rpm",
                data_type="integer",
                description="Engine speed",
            )
            db.add(signal)
            db.flush()

        if created_vehicle:
            db.add(
                Event(
                    vehicle_id=vehicle.id,
                    ecu_id=ecu.id,
                    signal_id=signal.id,
                    event_type="SIGNAL_SAMPLE",
                    payload={"value": 742, "source": "seed"},
                )
            )

        db.commit()
        print("Seed data ready: admin user, sample vehicle, ECU, signal, and event.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
