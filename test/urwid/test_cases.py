"""Tests whether the script correctly handles multiline arguments and verifies
directory structure."""

# def test_case_sensitivity():
#     assert match_pattern("A*t", ["Apple", "apricot", "Avocado"]) == ["apricot"]


# def test_multiple_matches_with_wildcard():
#     assert match_pattern("a*c", ["abc", "adc", "aec"]) == ["abc", "adc", "aec"]


# def test_wildcard_at_start():
#     assert match_pattern("*cot", ["apple", "apricot", "avocado"]) == ["apricot"]


# def test_multiple_wildcards_complex():
#     assert match_pattern("a*d*o", ["avocado", "apricot", "ado"]) == [
#         "avocado",
#         "ado",
#     ]


# def test_empty_list():
#     assert match_pattern("a*t", []) == []


# def test_pattern_longer_than_words():
#     assert match_pattern("a*plez", ["apple", "apricot", "avocado"]) == []


# def test_only_wildcard():
#     assert match_pattern("*", ["apple", "apricot", "avocado"]) == [
#         "apple",
#         "apricot",
#         "avocado",
#     ]


# def test_consecutive_wildcards():
#     assert match_pattern("a**e", ["apple", "apricot", "avocado"]) == ["apple"]


# def test_single_letter():
#     assert match_pattern("a", ["apple", "apricot", "avocado"]) == [
#         "apple",
#         "apricot",
#         "avocado",
#     ]


# def test_non_alphanumeric():
#     assert match_pattern("a*t!", ["apple", "apricot!", "avocado"]) == [
#         "apricot!"
#     ]


# # from tui_labeller import main  # Assuming main is the entry point


# def test_single_letter_wildcard():
#     assert match_pattern("a*t", ["apple", "apricot", "avocado"]) == ["apricot"]


# def test_single_letter_prefix():
#     assert match_pattern("a*", ["apple", "apricot", "avocado"]) == [
#         "apple",
#         "apricot",
#     ]


# def test_multiple_wildcards():
#     assert match_pattern("a*o", ["apple", "apricot", "avocado"]) == ["avocado"]


# def test_exact_prefix():
#     assert match_pattern("av", ["apple", "apricot", "avocado"]) == ["avocado"]


# def test_no_match():
#     assert match_pattern("b*t", ["apple", "apricot", "avocado"]) == []


# def test_empty_pattern():
#     assert match_pattern("", ["apple", "apricot", "avocado"]) == [
#         "apple",
#         "apricot",
#         "avocado",
#     ]


# def test_full_word():
#     assert match_pattern("apple", ["apple", "apricot", "avocado"]) == ["apple"]


# def test_wildcard_at_end():
#     assert match_pattern("ap*", ["apple", "apricot", "avocado"]) == [
#         "apple",
#         "apricot",
#     ]
