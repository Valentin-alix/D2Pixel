from D2Shared.shared.schemas.equipment import ReadEquipmentSchema, UpdateEquipmentSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

EQUIPMENT_URL = BACKEND_URL + "/equipment/"


class EquipmentService:
    @staticmethod
    async def get_equipments(service: ClientService) -> list[ReadEquipmentSchema]:
        resp = await service.session.get(f"{EQUIPMENT_URL}")
        return [ReadEquipmentSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def create_equipment(
        service: ClientService,
        equipment_datas: UpdateEquipmentSchema,
    ) -> ReadEquipmentSchema:
        resp = await service.session.post(
            f"{EQUIPMENT_URL}", json=equipment_datas.model_dump()
        )
        return ReadEquipmentSchema(**resp.json())

    @staticmethod
    async def update_equipment(
        service: ClientService,
        equipment_id: int,
        equipment_datas: UpdateEquipmentSchema,
    ) -> ReadEquipmentSchema:
        resp = await service.session.put(
            f"{EQUIPMENT_URL}{equipment_id}", json=equipment_datas.model_dump()
        )
        return ReadEquipmentSchema(**resp.json())

    @staticmethod
    async def increment_count_achieved(
        service: ClientService,
        equipment_id: int,
    ) -> ReadEquipmentSchema:
        resp = await service.session.put(
            f"{EQUIPMENT_URL}{equipment_id}/count_lines_achieved/"
        )
        return ReadEquipmentSchema(**resp.json())

    @staticmethod
    async def delete_equipment(service: ClientService, equipment_id: int) -> None:
        await service.session.delete(f"{EQUIPMENT_URL}{equipment_id}")
        return None
