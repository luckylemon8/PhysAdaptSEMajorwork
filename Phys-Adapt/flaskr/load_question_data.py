import csv

csvfile = open("flaskr/questions.csv", newline="")
c = csv.DictReader(csvfile)

for row in c:
    statement = (
        "INSERT INTO question ('question_title', 'question_image', 'id', 'answer', 'band', 'recommended_time', 'module') VALUES ('"
        + str(row["Question title"])
        + "','"
        + str("/static/images/questions/" + row["Question title"] + ".png")
        + "','"
        + str(row["ID"])
        + "','"
        + str(row["Answer"])
        + "',"
        + str(row["Band"])
        + ","
        + str(row["recommended time"])
        + ","
        + str(row["Module"])
        + ");"
    )
    print(statement)
# save and close the file
csvfile.close()
