def quick_sort(lst):
    if len(lst) <= 1:
        return lst
    smaller = [x for x in lst[1:] if x < lst[0]]
    larger = [x for x in lst[1:] if x >= lst[0]]
    return quick_sort(smaller) + [lst[0]] + quick_sort(larger)


# Main Function
if __name__ == '__main__':
    lst = [2, 4, 5, 1]
    print(quick_sort(lst))
