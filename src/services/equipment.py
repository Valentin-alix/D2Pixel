from D2Shared.shared.schemas.equipment import ReadEquipmentSchema, UpdateEquipmentSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

EQUIPMENT_URL = BACKEND_URL + "/equipment/"


class EquipmentService:
    @staticmethod
    def get_equipments(service: ServiceSession) -> list[ReadEquipmentSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{EQUIPMENT_URL}")
            return [ReadEquipmentSchema(**elem) for elem in resp.json()]

    @staticmethod
    def create_equipment(
        service: ServiceSession,
        equipment_datas: UpdateEquipmentSchema,
    ) -> ReadEquipmentSchema:
        with service.logged_session() as session:
            resp = session.post(f"{EQUIPMENT_URL}", json=equipment_datas.model_dump())
            return ReadEquipmentSchema(**resp.json())

    @staticmethod
    def update_equipment(
        service: ServiceSession,
        equipment_id: int,
        equipment_datas: UpdateEquipmentSchema,
    ) -> ReadEquipmentSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{EQUIPMENT_URL}{equipment_id}", json=equipment_datas.model_dump()
            )
            return ReadEquipmentSchema(**resp.json())

    @staticmethod
    def increment_count_achieved(
        service: ServiceSession,
        equipment_id: int,
    ) -> ReadEquipmentSchema:
        with service.logged_session() as session:
            resp = session.put(f"{EQUIPMENT_URL}{equipment_id}/count_lines_achieved/")
            return ReadEquipmentSchema(**resp.json())

    @staticmethod
    def delete_equipment(service: ServiceSession, equipment_id: int) -> None:
        with service.logged_session() as session:
            session.delete(f"{EQUIPMENT_URL}{equipment_id}")
            return None
