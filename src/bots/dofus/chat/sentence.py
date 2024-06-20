from faker import Faker


class FakeSentence:
    faker = Faker("fr_FR")

    def get_random_sentence(self) -> str:
        return self.faker.sentence()
