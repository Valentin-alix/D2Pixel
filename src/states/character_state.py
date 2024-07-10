from D2Shared.shared.schemas.character import CharacterSchema
from src.services.character import CharacterService
from src.services.session import ServiceSession


class CharacterState:
    def __init__(self, service: ServiceSession, character_id: str) -> None:
        self._character: CharacterSchema | None = None
        self.service = service
        self.character_id = character_id
        self.pods = CharacterService.get_max_pods(self.service, self.character.id)

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
