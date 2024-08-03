from dataclasses import dataclass, field

from D2Shared.shared.schemas.character import CharacterSchema
from src.services.character import CharacterService
from src.services.session import ServiceSession


@dataclass
class CharacterState:
    service: ServiceSession
    character_id: str
    pods: int = field(init=False)
    _character: CharacterSchema | None = field(default=None, init=False)

    def __post_init__(self):
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
