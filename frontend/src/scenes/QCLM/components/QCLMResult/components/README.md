# Ratio Counter explanation

- Input: list of MSDM records
- Output: list of MSDM records with ratio information

## Algorithm

- separate mutations by siteId (mutation position)
  - in case there are more mutation sites in one record, sort site numbers an
    join them to string, this ensures we have same site ID for mutations on same
    position
- compute mutations per site
  - get number of unique mutation targets per every position
  - get ratio per position in one mutation
    - number of targets / number of all targets on position
  - multiply mutation ratio on every position
    - ratio on position 1 \* ratio on position 2 ... = ratio for mutation
