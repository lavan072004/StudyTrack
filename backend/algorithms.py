from typing import List, Dict, Any, Tuple


def insertion_sort_by_age(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sorts a list of student dictionaries by Age using custom Insertion Sort algorithm.
    Time Complexity:
      Best Case: O(n) - when already sorted
      Worst Case: O(n^2) - when sorted in reverse order
    """
    arr = list(students)
    n = len(arr)
    
    for i in range(1, n):
        key_item = arr[i]
        j = i - 1
        while j >= 0 and arr[j]["age"] > key_item["age"]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key_item
        
    return arr


def insertion_sort_by_name(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sorts a list of student dictionaries by Name using custom Insertion Sort algorithm.
    Required prerequisite for Binary Search on Name.
    """
    arr = list(students)
    n = len(arr)
    
    for i in range(1, n):
        key_item = arr[i]
        j = i - 1
        while j >= 0 and arr[j]["name"].lower() > key_item["name"].lower():
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key_item
        
    return arr


def binary_search_by_name(students: List[Dict[str, Any]], target_name: str) -> Tuple[List[Dict[str, Any]], int]:
    """
    Searches for a student by Name using custom Binary Search algorithm.
    Returns a tuple of (matched_students_list, matched_index).
    If no match is found, returns ([], -1).
    """
    if not students or not target_name:
        return [], -1
        
    # Binary Search requires a sorted array by Name
    sorted_students = insertion_sort_by_name(students)
    
    low = 0
    high = len(sorted_students) - 1
    target_clean = target_name.strip().lower()
    
    matches = []
    found_idx = -1
    
    while low <= high:
        mid = (low + high) // 2
        mid_name_clean = sorted_students[mid]["name"].strip().lower()
        
        if mid_name_clean == target_clean:
            found_idx = mid
            matches.append(sorted_students[mid])
            
            # Check adjacent left elements for duplicate names
            left = mid - 1
            while left >= 0 and sorted_students[left]["name"].strip().lower() == target_clean:
                matches.append(sorted_students[left])
                left -= 1
                
            # Check adjacent right elements for duplicate names
            right = mid + 1
            while right < len(sorted_students) and sorted_students[right]["name"].strip().lower() == target_clean:
                matches.append(sorted_students[right])
                right += 1
                
            return matches, found_idx
        elif mid_name_clean < target_clean:
            low = mid + 1
        else:
            high = mid - 1
            
    return [], -1


def generate_student_report(students: List[Dict[str, Any]]) -> List[str]:
    """
    Generates a report formatted as:
      Age 19 - Rohan
      Age 20 - Farhan
      Age 21 - Priya
    Sorted by age using Insertion Sort.
    """
    sorted_students = insertion_sort_by_age(students)
    report = []
    for s in sorted_students:
        report.append(f"Age {s['age']} - {s['name']}")
    return report
