DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS quiz;
DROP TABLE IF EXISTS question_response;
DROP TABLE IF EXISTS error_scores;
DROP TABLE IF EXISTS question;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE error_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  mod_5_error_score INTEGER NOT NULL,
  mod_6_error_score INTEGER NOT NULL,
  mod_7_error_score INTEGER NOT NULL,
  mod_8_error_score INTEGER NOT NULL,
  updated_date_time DATE NOT NULL
);

CREATE TABLE quiz (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date_completed DATE
);

CREATE TABLE question_response (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  quiz_id INTEGER NOT NULL,
  question_id INTEGER NOT NULL,
  answer TEXT,
  question_number INTEGER 
);

CREATE TABLE question (
  id INTEGER PRIMARY KEY,
  question_title TEXT NOT NULL,
  question_image TEXT NOT NULL,
  answer TEXT NOT NULL,
  band INTEGER NOT NULL,
  recommended_time INTEGER NOT NULL,
  module INTEGER NOT NULL
);

