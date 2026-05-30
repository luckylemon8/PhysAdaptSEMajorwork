import csv

csvfile = open("flaskr/questions.csv", newline="")
c = csv.DictReader(csvfile)

print(
    "INSERT INTO user (username, password) VALUES ('test', 'scrypt:32768:8:1$rCnqWv54lWPHqwHl$670f919bf8338cff891a45c5112dd059b271c0933722987135797c25eddf14fb6f0562e54737e3f00b4d65328ffeae5c12360990ca6de2d28bd25a734a2d7b4c');"
)

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
