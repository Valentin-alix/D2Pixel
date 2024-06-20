from EzreD2Shared.shared.schemas.character import CharacterSchema

from src.services.character import CharacterService


class CharacterState:
    pods: int

    def __init__(self, character_id: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._character: CharacterSchema | None = None
        self.in_fight: bool = False
        self.is_dead: bool = False
        self.character_id = character_id
        self.pods = CharacterService.get_max_pods(self.character.id)

    @property
    def character(self) -> CharacterSchema:
        if self._character is None:
            self._character = CharacterService.get_or_create_character(
                self.character_id
            )
        return self._character

    @character.setter
    def character(self, value: CharacterSchema):
        self._character = value
