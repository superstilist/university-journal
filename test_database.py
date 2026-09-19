import os
import unittest
import database

TEST_DB = "test_university.db"


class TestUniversityDatabase(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        database.init_db(TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_add_and_get_students(self):
        s_id = database.add_student("Іван Іваненко", 20, "Фізика", db_name=TEST_DB)
        students = database.get_all_students(db_name=TEST_DB)
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0]["name"], "Іван Іваненко")

        student = database.get_student_by_id(s_id, db_name=TEST_DB)
        self.assertIsNotNone(student)
        self.assertEqual(student["major"], "Фізика")

    def test_add_and_get_courses(self):
        c_id = database.add_course("Вища математика", "проф. Іванов", db_name=TEST_DB)
        courses = database.get_all_courses(db_name=TEST_DB)
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]["course_name"], "Вища математика")

    def test_update_student_and_course(self):
        s_id = database.add_student("Петро", 19, "Математика", db_name=TEST_DB)
        updated = database.update_student(s_id, "Петро Петренко", 20, "Інформатика", db_name=TEST_DB)
        self.assertTrue(updated)
        student = database.get_student_by_id(s_id, db_name=TEST_DB)
        self.assertEqual(student["name"], "Петро Петренко")
        self.assertEqual(student["age"], 20)

        c_id = database.add_course("Фізика", "доц. Петров", db_name=TEST_DB)
        updated_c = database.update_course(c_id, "Загальна Фізика", "доц. Петров О.", db_name=TEST_DB)
        self.assertTrue(updated_c)

    def test_enrollment_and_join_queries(self):
        s1 = database.add_student("Студент 1", 20, "CS", db_name=TEST_DB)
        s2 = database.add_student("Студент 2", 21, "CS", db_name=TEST_DB)
        c1 = database.add_course("Курс 1", "Викладач 1", db_name=TEST_DB)

        self.assertTrue(database.enroll_student(s1, c1, db_name=TEST_DB))
        self.assertTrue(database.enroll_student(s2, c1, db_name=TEST_DB))
        # Duplicate enrollment should fail
        self.assertFalse(database.enroll_student(s1, c1, db_name=TEST_DB))

        students_in_c1 = database.get_students_in_course(c1, db_name=TEST_DB)
        self.assertEqual(len(students_in_c1), 2)
        names = [s["name"] for s in students_in_c1]
        self.assertIn("Студент 1", names)
        self.assertIn("Студент 2", names)

        c_for_s1 = database.get_courses_for_student(s1, db_name=TEST_DB)
        self.assertEqual(len(c_for_s1), 1)
        self.assertEqual(c_for_s1[0]["course_name"], "Курс 1")


if __name__ == "__main__":
    unittest.main()
