from faker import Faker


class FakeSentence:
    _faker = Faker("fr_FR")

    def get_random_sentence(self) -> str:
        return self._faker.sentence()
