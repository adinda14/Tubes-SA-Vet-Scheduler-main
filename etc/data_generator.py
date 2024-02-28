"""
Vet Scheduler data generator
"""

import random as rd
from pprint import pprint

DATA_COUNT = 30

D_SERVICES = [
    # * Nama, Prioritas, Max Waktu
    ("sick visit", 2, 40),
    ("wellness exam", 1, 20),
    ("vaccination", 2, 30),
    ("microchipping", 2, 180),
    ("ultrasound", 1, 60),
    ("dentistry", 2, 60),
    ("neuter", 4, 180),
    ("radiology", 3, 240),
]


def rounding(data, multiple):
    """
    Rounding to closest multiple num
    """
    return multiple * round(data / multiple)


def generator(data_count=DATA_COUNT) -> list:
    """
    Generate data
    """
    generated_list = []
    counter = 0
    while counter < data_count:
        service, priority, max_time = rd.choice(D_SERVICES)
        new_data = (service,
                    rounding(rd.randint(10, max_time), 5),
                    rounding(rd.randint(10, max_time), 5),
                    priority)

        if new_data in generated_list:
            continue

        generated_list.append(new_data)
        counter += 1
    return generated_list


if __name__ == "__main__":
    result = generator()
    pprint(result)
