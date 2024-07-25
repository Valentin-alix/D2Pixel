from D2Shared.shared.schemas.character import CharacterSchema
from src.services.character import CharacterService
from src.services.client_service import ClientService


class CharacterState:
    def __init__(self, service: ClientService, character_id: str) -> None:
        self._character: CharacterSchema | None = None
        self.service = service
        self.character_id = character_id
        self.pods = self.character.max_pods

    @property
    def character(self) -> CharacterSchema:
        if self._character is None:
            self._character = CharacterService.get_or_create_character(
                self.service, self.character_id
            )
        return self._character

    @character.setter
    def character(self, value: CharacterSchema):
        self._character = value
