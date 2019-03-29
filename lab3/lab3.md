# Levenshtein distance and spelling corrections

The task introduces the Levenshtein distance - a measure that is useful in tasks such as approximate string matching.

## Tasks

1. Use ElasticSearch term vectors API to retrieve and store for each document the following data:
   1. The terms (tokens) that are present in the document.
   2. The number of times given term is present in the document.
1. Aggregate the result to obtain one global **frequency list**.
1. Filter the list to keep terms that contain only letters and have at least 2 of them.
1. Make a plot in a logarithmic scale:
   1. X-axis should contain the **rank** of a term, meaning the first rank belongs to the term with the highest number of
      occurrences; the terms with the same number of occurrences should be ordered by their name,
   2. Y-axis should contain the **number of occurrences** of the term with given rank.
1. Download [polimorfologik.zip](https://github.com/morfologik/polimorfologik/releases/download/2.1/polimorfologik-2.1.zip) dictionary
   and use it to find all words that do not appear in that dictionary.
1. Find 30 words with the highest ranks that do not belong to the dictionary.
1. Find 30 words with 3 occurrences that do not belong to the dictionary.
1. Use Levenshtein distance and the frequency list, to determine the most probable correction of the words from the
   second list.

## Hints

1. Levenshtein distance (Edit distance) is a measure defined for any pair of strings. It is defined as the minimal
   number of single character edits (insertions, deletions or substitutions) needed to transform one string to the
   other. The measure is symmetric.
1. The algorithm is usually implemented as a dynamic program, see [Wikipedia article](https://en.wikipedia.org/wiki/Levenshtein_distance) 
   for details.
1. The distance may be used to fix an invalid word by inspecting in the growing order of the distance, the words
   that are *n* edits away from the invalid word. If there are no words *n* edits away, the words *n+1* edits away 
   are inspected.
1. The frequency list may be used to select the most popular word with given distance, if there are many candidate
   corrections.
1. Usually the correction algorithm does not use the edit distance directly, since it would require to compare the
   invalid word with all words in the dictionary. The algorithms work in the opposite way - the generate candidate words
   that are 1 or 2 edits away from the invalid word (cf. P. Norvigs [article](https://norvig.com/spell-correct.html) 
   for the details). A different approach is to use [Levenshtein automaton](https://norvig.com/spell-correct.html) for
   finding the corrections effectively.
1. ElasticSearch has a [fuzziness](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html)
   parameter for finding approximate matches of a query.
