# OCAT
**Optimal categories assignment for table columns**

The solution helps to find optimal way to assign categories to columns having likelihood scores for each column in a table.
To make it fast and be able to assign any constrains needed, we are using approaches from Linear Algebra and Graph Theory.
Comparing to naive brute force approach the solution shows exponential improvement in the running time.
The larger input table size, the bigger difference in performance. For the table of 8 columns and 7 possible categories it already uses only 0.2414% of all possible cobinations to find optimal solution.

## Setup
1. Creat project environment (venv, conda, etc.)
2. Install dependencies from `requirenments.txt`:
```shell
pip install -r "requirements.txt"
```

## Run tests
Run tests to validated that everything works properly.
4 test should pass in approximately 0.8 seconds.
```shell
pytest
```

## Run on your data
Specify paths in the `config.ini`:
1. path to the input table or select one from the `cases` folder
2. path to the corresponding adjacency matrix
3. path to the corresponding rules matrix
4. column categories that should be present in the final result (must-have categories) 

Below in the 'Setting constrains' section you could find details on how to prepare adjacency matrix and rules matrix. 

When you are done, run
```shell
python3 main.py
```

## Setting constrains
To set constrains on the columns categories positions we only need two matrices - Adjacency matrix and Rules matrix.
Read below how to construct them.

Current constrains are,
1. Each column type can be assigned only once except the 'Other' type. It can be assigned to multiple columns.
2. Types 'Description' and 'CurrentAmount' must be assigned.
3. 'Description' column must be placed to the left of the non-'Other' columns.
4. If we have both 'CurrentHours' and 'YtdHours' types then 'CurrentHours' must be placed to the left of 'YtdHours'.
5. If we have both 'CurrentAmount' and 'YtdAmount' types then 'CurrentAmount' must be placed to the left of 'YtdAmount'.

### Adjacency matrix
Here you can find details on the Adjacency matrix structure.

Column names in the adjacency matrix are the same as the row names on the same position.
For example, 
- if the third row named Rate, then the third colum would be also name Rate.

It's a square matrix that has value 1 if the category could be right before another category, and 0 otherwise. For example,
- if Rate could be right before CurrentHours, then value on the intersection of Rate row and CurrentHours column should be 1;
- if Rate couldn't be right before Description, then value on the intersection of Rate row and Description column should be 0;
- 'Other' category couldn't be right before 'YtdAmount' category (since there are must be 'Description' and 'CurrentAmount' in between), hence Adjacency matrix has 0 on the intersection of 'Other' row and 'YtdAmount' column.

### Rules matrix
The idea behind the Rules matrix, is very similar to the Adjacency matrix with one distinction.
It's just not that strict. 
It has 1, if category could be on **any** place before another category
(unlike, Adjacency matrix, where it only says that category couldn't be just right before another category).
We don't even care if it could stand right before another category or not. We just care if it could stand **anywhere** before. 
For example,
- Unlike the third example from Adjacency matrix idea explanation (where 'Other' category couldn't be right before 'YtdAmount' category), in the Rules matrix we should have 1 on the intersection of 'Other' row and 'YtdAmount' column. Because 'Other' category could stand anywhere before 'YtdAmount'.

## Release history:
- v1.0 - graph based solution


## TODO:
- add parallelization
- add tests for the bad input in the Input table, Adjacency matrix and Rules matrix 
- add images for Adjacency matrix and Rules matrix explanation
