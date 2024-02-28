import argparse
import io
import sys
import time

from dataclasses import dataclass
from pprint import pprint

from etc.data_sample import sample_1, sample_2, sample_3, sample_4


@dataclass
class KnapsackD:
    """Knapsack data"""
    cap: int
    data: list
    data_count: int
    k: int

    def __init__(self, cap, data):
        self.cap: int = cap
        self.data: list = data
        self.data_count: int = len(data)
        self.k: int = 0

        temp = 0
        for _, val in enumerate(self.data):
            self.k += 1
            temp += val[2]
            if temp >= self.cap:
                break


def prep(source):
    """
    * 1. Hitung rasio tiap elemen
    * 2. Bagi tiap elemen berdasarkan prioritas
    * 3. Urutkan tiap prioritas berdasarkan rasio
    """
    max_prio = max(source, key=lambda x: x[3])[3]
    tabel_prio = [[] for _ in range(max_prio)]

    for data in source:
        # ? Add rasio
        (nama, profit, waktu, prioritas) = data
        rasio = profit / waktu
        data_baru = (nama, profit, waktu, prioritas, rasio)

        # ? Bagi data berdasarkan prioritas
        tabel_prio[prioritas-1].append(data_baru)

    # ? Urut berdasarkan rasio
    for index, item_list in enumerate(tabel_prio):
        tabel_prio[index] = sorted(item_list,
                                   key=lambda x: x[4],
                                   reverse=True)

    print("\nTabel Prioritas:")
    pprint(tabel_prio)
    print()

    return (tabel_prio, max_prio)


def get_bound(k: KnapsackD, depth, profit, weight):
    """
    * Hitung bound berdasarkan rumus bound pada slide perkuliahan
    """
    next_depth = depth + 1
    last_sel = min(k.k, k.data_count)

    tot_wg = weight + sum(x[2]
                          for x
                          in k.data[next_depth:last_sel])
    bound = (profit + sum(x[1]
                          for x
                          in k.data[next_depth:last_sel])
             + ((k.cap - tot_wg) * k.data[last_sel-1][4]))
    return bound


def find(k: KnapsackD, marks: list, depth: int, insert_child: bool,
         profit, weight, max_profit, item_count):
    """
    * Memproses elemen pada kedalaman {depth}
    * {marks} merupakan penanda masuk atau tidaknya elemen
    *   pada kedalaman sebelumnya
    * Penanda pada {marks} pada kedalaman {depth} akan
    *   dimasukkan "1" jika {insert_child} = True.
    *   Jika tidak, maka "0" dimasukkan
    * {profit} merupakan profit untuk setiap elemen yang dimasukkan
    *   sesuai dengan elemen yang ditandai {marks}
    * {max_profit} merupakan profit terbesar yang pernah ditemukan,
    *   terlepas dari elemen yang ditandai {marks}
    """
    # ? Check depth passed limit
    if depth > (k.data_count):
        return None

    # ? New data
    current_marks = marks
    current_profit = profit
    current_weight = weight
    current_max_profit = max_profit

    current_marks.append(int(insert_child))

    marks_left = []
    marks_right = []
    _mark = []

    for mark in current_marks:
        marks_left.append(mark)
        marks_right.append(mark)
        _mark.append(str(mark))

    print(f"Depth: {depth:>3} | Marks: {(' '.join(_mark)):<30}", end="")
    print(f"Depth: {depth:>3} | "
          f"Marks: {format((' '.join(_mark)), f'<{item_count * 2 - 1}')}",
          end="")

    # ? Check if data should be inserted
    if insert_child:
        # ? Add data
        current_profit += k.data[depth-1][1]
        current_weight += k.data[depth-1][2]

        # ? Update max profit
        if current_profit > current_max_profit:
            current_max_profit = current_profit

    # ? Get bound value
    bound = get_bound(k, depth, current_profit, current_weight)

    # ? Check promising status
    # * Non Promising:
    # *     1. Bound <= Max Profit
    # *     2. current_weight > W       // W = max capacity
    promising = (bound > max_profit) and (current_weight <= k.cap)

    current = (current_marks, current_profit, current_weight,
               current_max_profit, promising)
    next_depth = depth + 1

    print(" | "
          f"p = {current_profit:>4}; "
          f"w = {current_weight:>4}; "
          f"cap = {k.cap}",
          end="")

    # ? Check if promising, otherwise stop generating childs
    if not promising:
        print(" (UNPROMISING)")
        return current

    elif depth >= k.data_count:
        print(" (Max depth reached)")

    else:
        print()

    # ? Generate childs
    result_left = find(k, marks_left, next_depth, True, current_profit,
                       current_weight, current_max_profit, item_count)
    result_right = find(k, marks_right, next_depth, False, current_profit,
                        current_weight, current_max_profit, item_count)

    return max([data
                for data in [current, result_left, result_right]
                if data             # ? <- only process non-empty data
                if data[4]],        # ? <- only count promising set
               key=lambda x: x[3])  # ? <- find max profit


def knapsack(cap, data, item_count):
    """
    * Main Knapsack function
    """
    optimal = None
    marks_left = []
    marks_right = []
    k = KnapsackD(cap, data)

    # ? (Child) Left - Inserted
    r_result_left = find(k, marks_left, 1, True, 0, 0, 0, item_count)
    print(f"    Max left: {r_result_left}\n")

    # ? (Child) Right - Not Inserted
    r_result_right = find(k, marks_right, 1, False, 0, 0, 0, item_count)
    print(f"    Max right: {r_result_right}\n")

    try:
        optimal = max([data
                       for data in [r_result_left, r_result_right]
                       if data
                       if data[4]],
                      key=lambda x: x[3])
        print(f"Optimal: {optimal}")

    except ValueError:
        print("No possible solution")
        pass

    return optimal


def scheduler(source=sample_1, limit=24*60):
    """
    * Main program function
    """
    data_count = len(source)
    data, max_prio = prep(source)
    marks = [[] for _ in range(max_prio)]
    results = [[] for _ in range(max_prio)]
    c_limit = limit - 0
    max_profit = 0
    max_weight = 0
    selected_count = 0

    if not args.details:
        sys.stdout = io.StringIO()

    time_start = time.perf_counter()

    for prio_index, item_list in enumerate(reversed(data)):
        list_item_count = len(item_list)
        if c_limit <= 0:
            if c_limit < 0:
                print("[!!!] overloaded")
            break

        print(f"\nPriority: {max_prio - prio_index} | "
              f"item count: {list_item_count}")
        print("=" * 30)

        # ? Process data
        result = knapsack(c_limit, item_list, list_item_count)

        if not result:
            print("No results found")
            continue

        # ? Extract data
        marks[prio_index], profit, weight, _, _ = result
        results[prio_index] = [item_list[i]
                               for i, val in enumerate(marks[prio_index])
                               if val]
        c_limit -= weight
        max_weight += weight
        max_profit += profit

    time_end = time.perf_counter()
    time_running = time_end - time_start

    if not args.details:
        sys.stdout = sys.__stdout__

    print("\nResults:")

    for prio_index, item_list in enumerate(results):
        item_count = len(item_list)
        selected_count += item_count
        prio = max_prio - prio_index
        print(f"Priority ({prio}): "
              f"Selected {item_count} / {len(data[prio-1])}",
              end="")

        if item_count >= 1:
            print(f" (Select mark: {marks[prio_index]})\n"
                  "  Items:")

            for item in item_list:
                nama, profit, waktu, _, rasio = item
                print(f"    {nama} "
                      f"(Profit {profit:>3}; "
                      f"Waktu {waktu:>3}; "
                      f"Rasio {rasio:>3.4})")

        print("" if item_count >= 1 else "\n")

    print("\n"
          f"Max Profit: {max_profit} | "
          f"Weight: {max_weight} ({c_limit} left from {limit})"
          "\n"
          f"Running time for {data_count} data(s): {time_running} sec")


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("-d", "--details", help="Show process details", action="store_true", default=False)
    args = argp.parse_args()

    _sources = [sample_1, sample_2, sample_3, sample_4]
    _sources_l = len(_sources)

    while True:
        try:
            _selector = int(input(f"Data sample selector (1 to {_sources_l}): "))
            _limit = int(input("Schedule (Knapsack) limit (in minutes): "))

            if (_selector < 1) or (_selector > _sources_l) or (_limit <= 0):
                raise ValueError

        except ValueError:
            exit()

        _source = _sources[_selector - 1]

        scheduler(_source, _limit)
        print()
        print("=" * 30)
        print()
