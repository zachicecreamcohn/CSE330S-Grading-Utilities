# Push Grades to Canvas

## Running

You will want to export the entire canvas gradebook first and then put it in this folder.

Make sure to put the scraped grades csv in here too after running get_grades_from_repos.py

```bash
python main.py <csv with grades> <canvas csv export> scraper
```

It will output a csv named "name-of-canvas-gradebook-file"-OUTPUT.csv

Then copy the second and third lines of the imported gradebook csv and copy into the output file (in the same spot) so that canvas can read the file correctly.

Now you can import the output file into canvas and the grades will populate in canvas. Make sure to "post" grades so that students can see them.