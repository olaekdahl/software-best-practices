# LSP/ISP (bad): broken substitution & fat interface
# Talking points:
# - Base demands fly(); some subtypes can’t → LSP broken.
# - Fat interface forces capabilities; throws at runtime.
#
# Anti-pattern:
# - A base type (Animal) demands fly() even for animals that cannot fly.
#   Subtypes like Penguin must throw at runtime → LSP violation.
# - One fat interface forces capabilities on all subtypes.
from abc import ABC, abstractmethod


class Animal(ABC):
    @abstractmethod
    def fly(self) -> None: ...


class Bird(Animal):
    def fly(self) -> None:
        print("Bird flying")


class Penguin(Bird):  # not actually a flying bird
    def fly(self) -> None:
        # Violates LSP: subtype can't honor base contract
        raise NotImplementedError("Penguins cannot fly")


def make_it_fly(animal: Animal) -> None:
    # Expectation: any Animal can fly (bad design). The contract itself is wrong.
    animal.fly()


if __name__ == "__main__":
    make_it_fly(Bird())
    try:
        make_it_fly(Penguin())  # runtime failure → LSP broken
    except NotImplementedError as e:
        print(f"LSP violation at runtime: {e}")
