from typing import List, Dict, Any, Tuple


def insertion_sort_by_field(students: List[Dict[str, Any]], field: str = "age") -> List[Dict[str, Any]]:
    """
    Sorts a list of student dictionaries by specified field ("age" or "name")
    using custom manual Insertion Sort algorithm.
    Time Complexity:
      Best Case: O(n) - when input is already sorted
      Worst Case: O(n^2) - when input is sorted in reverse order
    """
    arr = list(students)
    n = len(arr)

    for i in range(1, n):
        key_item = arr[i]
        j = i - 1

        if field == "name":
            key_val = str(key_item.get("name", "")).strip().lower()
            while j >= 0 and str(arr[j].get("name", "")).strip().lower() > key_val:
                arr[j + 1] = arr[j]
                j -= 1
        else:  # default "age"
            key_val = key_item.get("age", 0)
            while j >= 0 and arr[j].get("age", 0) > key_val:
                arr[j + 1] = arr[j]
                j -= 1

        arr[j + 1] = key_item

    return arr


def binary_search_by_name(sorted_students: List[Dict[str, Any]], target_name: str) -> List[Dict[str, Any]]:
    """
    Searches for a student by Name using custom handwritten iterative Binary Search.
    PREREQUISITE: Expects an ALREADY name-sorted list of students. Does NOT sort inside.
    Uses EXACT formula: mid = low + (high - low) // 2
    """
    if not sorted_students or not target_name:
        return []

    target_clean = target_name.strip().lower()
    low = 0
    high = len(sorted_students) - 1
    matches = []

    while low <= high:
        # EXACT required mid formula
        mid = low + (high - low) // 2
        mid_name = str(sorted_students[mid].get("name", "")).strip().lower()

        if mid_name == target_clean:
            matches.append(sorted_students[mid])

            # Expand left for duplicate names
            left = mid - 1
            while left >= 0 and str(sorted_students[left].get("name", "")).strip().lower() == target_clean:
                matches.append(sorted_students[left])
                left -= 1

            # Expand right for duplicate names
            right = mid + 1
            while right < len(sorted_students) and str(sorted_students[right].get("name", "")).strip().lower() == target_clean:
                matches.append(sorted_students[right])
                right += 1

            return matches
        elif mid_name < target_clean:
            low = mid + 1
        else:
            high = mid - 1

    return matches


def count_students_meeting_min_age(students: List[Dict[str, Any]], min_age: int) -> int:
    """
    Counts students meeting minimum age requirement using explicit loop.
    Requirement 14: Do NOT implement this only as sum(1 for ...).
    """
    count = 0
    for s in students:
        if s.get("age", 0) >= min_age:
            count += 1
    return count


def generate_student_report(students: List[Dict[str, Any]], min_age: int = 21) -> Tuple[List[str], int]:
    """
    Generates report formatted as:
      [Age X] Name <email>
    Only includes students with age >= min_age, sorted by age using Insertion Sort.
    Returns (report_lines, count_meeting_min_age).
    """
    sorted_students = insertion_sort_by_field(students, field="age")
    report_lines = []

    for s in sorted_students:
        age_val = s.get("age", 0)
        if age_val >= min_age:
            report_lines.append(f"[Age {age_val}] {s['name']} <{s['email']}>")

    count_meeting = count_students_meeting_min_age(students, min_age)
    return report_lines, count_meeting
