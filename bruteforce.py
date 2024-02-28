import argparse
import io
import sys
import time

from pprint import pprint

from etc.data_sample import sample_1, sample_2, sample_3, sample_4


def prep(source):
    """
    Prepare data
    """
    max_prio = max(source, key=lambda x: x[3])[3]
    tabel_prio = [[] for _ in range(max_prio)]

    for data in source:
        (_, _, _, prioritas) = data
        tabel_prio[prioritas-1].append(data)

    for index, item_list in enumerate(tabel_prio):
        tabel_prio[index] = item_list

    print("\nTabel Prioritas:")
    pprint(tabel_prio)
    print()

    return (tabel_prio, max_prio)


def count_pw(data_list):
    """
    Count profit & weight
    """
    total_profit = 0
    total_weight = 0

    for data in data_list:
        (_, profit, weight, _) = data
        total_profit += profit
        total_weight += weight

    return (total_profit, total_weight)


def bruteforce(data_list, weight_limit):
    """
    * Main bruteforce function
    """
    list_len = len(data_list)
    generated = [[] for _ in range(list_len)]
    max_sel = None
    max_set = None
    max_profit = 0
    max_weight = 0

    subset_count = 2 ** list_len
    sel_max_len = len(format(subset_count, "b")) - 1

    for i in range(1, subset_count):
        c_weight = 0
        c_profit = 0
        selector = format(i, f"0{sel_max_len}b")
        set_len = len(str(int(selector)))
        c_set = [data_list[p]
                 for p, v in enumerate(list(selector))
                 if int(v)]

        c_profit, c_weight = count_pw(c_set)

        print(f"Profit: {c_profit:>3}; Weight: {c_weight:>3}; set: ", end="")
        print(*c_set)
        print(selector)

        generated[set_len-1].append(c_set)

        if (c_weight <= weight_limit) and (c_profit > max_profit):
            max_set, max_profit, max_weight = (c_set, c_profit, c_weight)
            max_sel = selector

    print(f"\nMax: profit={max_profit}; "
          f"weight={max_weight}; "
          f"select={max_sel}")

    return (max_set, max_profit, max_weight)


def scheduler(source=sample_1, limit=24*60):
    """
    * Main program function
    """
    data_count = len(source)
    data, max_prio = prep(source)
    results = [[] for _ in range(max_prio)]
    c_limit = limit - 0
    max_profit = 0
    max_weight = 0
    selected_count = 0

    if not args.details:
        sys.stdout = io.StringIO()

    time_start = time.perf_counter()

    for prio_index, item_list in enumerate(reversed(data)):
        item_count = len(item_list)
        if c_limit <= 0:
            if c_limit < 0:
                print("[!!!] overloaded")
            break
        print(f"\nPriority: {max_prio - prio_index} | "
              f"item count: {item_count}")
        print("=" * 30)

        result = bruteforce(item_list, c_limit)

        if not result[0]:
            print("No results found")
            continue

        results[prio_index], profit, weight = result
        max_profit += profit
        max_weight += weight
        c_limit -= weight

    time_end = time.perf_counter()
    time_running = time_end - time_start

    if not args.details:
        sys.stdout = sys.__stdout__

    print("\nResults:")

    for prio_index, item_list in enumerate(results):
        item_count = len(item_list)
        selected_count += item_count
        prio = max_prio - prio_index
        print(f"Priority ({prio}): Selected {item_count} / {len(data[::-1][prio_index])}")

        if item_count >= 1:
            print("  Items:")

            for item in item_list:
                nama, profit, waktu, _ = item
                print(f"    {nama} (Profit {profit:>3}; Waktu {waktu:>3})")

        print()

    print("\n"
          f"Max Profit: {max_profit} | "
          f"Weight: {max_weight} ({c_limit} left from {limit})"
          "\n"
          f"Running time for {data_count} data(s): {time_running} s")


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
