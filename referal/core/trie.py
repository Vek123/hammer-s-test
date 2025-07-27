__all__ = ()

import random


class CodeTrieNode:
    def __init__(self, text='', leafs=0):
        self.text = text
        self.children = {}
        self.leafs = leafs


class CodePrefixTree:
    def __init__(self):
        self.root = CodeTrieNode()

    def insert(self, word: str) -> None:
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = CodeTrieNode(char)

            current.leafs += 1
            current = current.children[char]

    def starts_with(self, prefix: str) -> bool:
        current = self.root
        for char in prefix:
            if char not in current.children:
                return False

            current = current.children[char]

        return True

    def get_shortest_random(self, alphabet: set, length: int) -> str | None:
        alphabet_len = len(alphabet)
        combinations_len = len(alphabet) ** length
        word = ''
        current = self.root
        for i in range(length):
            combinations_len /= alphabet_len
            good_chars = set(
                filter(
                    lambda x: current.children[x].leafs < combinations_len,
                    current.children.keys(),
                ),
            )
            bad_chars = set(current.children.keys()).difference(good_chars)
            empty_chars = alphabet.difference(good_chars).difference(bad_chars)
            if i == length - 1 or empty_chars:
                choice_chars = empty_chars
            elif good_chars:
                choice_chars = good_chars
            else:
                return None

            choosen_char = random.choice(list(choice_chars))
            word += choosen_char

            current = current.children.get(
                choosen_char,
                CodeTrieNode(choosen_char),
            )

        return word
