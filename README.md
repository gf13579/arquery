
# Accelerated Reader Query (arquery)

A Python module to download details (title, author, word count) of all books read by a student on a school"s Accelerated Reader programme, 0hosted by [Renaissance](https://www.renaissance.com.au/practice/accelerated-reader/). 


## Usage/Examples

Usage:
```bash
arquery.py [-h] -u USERNAME [-p PASSWORD] -s SCHOOLID -w WEBSITE
```

Example:
```bash
arquery.py -u jbloggs123 -p Reading123 -s 1234567 -w https://auhosted0.renlearn.com.au
```

## Example output

```json
 [{"author": "Liz  Pichon",
  "book_number": "327379 EN",
  "title": "The Brilliant World of Tom Gates",
  "word_count": "15304"},
 {"author": "Liz  Pichon",
  "book_number": "327267 EN",
  "title": "Excellent Excuses (And Other Good Stuff)",
  "word_count": "17045"}]
  ```

