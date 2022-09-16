from dataclasses import dataclass


@dataclass
class Temperature(object):
    temp_c: float

    @property
    def temp_f(self):
        return self.temp_c * 2 + 30


