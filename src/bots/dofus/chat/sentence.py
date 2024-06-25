from faker import Faker
from pydantic import BaseModel, ConfigDict


class FakeSentence(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _faker = Faker("fr_FR")

    def get_random_sentence(self) -> str:
        return self._faker.sentence()
